import csv
import os
import random
import time
import math

def send_fake_data(send_data_func, duration, rate, immitate_teensy=False):
    """ Send artificial data over MQTT if no file is specified. Sends [rate] per second for [duration] seconds
        Some fields are filled in by DAS.js, so if data will go through DAS.js (i.e. serial_test.py)
        we don't want to send that data """
    start_time = round(time.time(), 2)
    gps_speed = 0
    # MHP Workshop location
    gps_lat = -37.908756
    gps_long = 145.13404
    # Degrees to a metre at this lattitude
    # http://www.csgnetwork.com/degreelenllavcalc.html
    metre_lat = 1 / 110994.73
    metre_long = 1 / 87941.14
    while True:
        current_time = round(time.time(), 2)
        total_time = round(current_time - start_time, 2)

        # Generate data message
        data = "gps=1"
        data += "&gps_lat=" + str(gps_lat)
        data += "&gps_long=" + str(gps_long)
        # Move up to 5 metres per second in both directions
        gps_lat += random.randint(0, 50) * 0.1 * metre_lat * rate
        gps_long += random.randint(0, 50) * 0.1 * metre_long * rate
        data += "&gps_alt=00&gps_course=00"
        gps_speed = random.random() * (total_time) + gps_speed
        data += "&gps_speed=" + str(gps_speed)
        data += "&gps_satellites=00"
        data += "&aX=00.0000&aY=00.0000&aZ=00.0000&gX=00.0000&"
        data += "gY=00.0000&gZ=00.0000"
        data += "&thermoC=25.00&thermoF=25.00"
        data += "&pot=100"
        data += "&reed_velocity=" + str(random.randint(0, 150))
        data += "&reed_distance=" + str(random.randint(0, 150))
        if not immitate_teensy:
            data += "&filename=test.csv"
            data += "&time=" + str(total_time * 1000)
            data += "&power=" + str(random.randint(0, 150))
            data += "&cadence=" + str(random.randint(0, 150))

        send_data_func(data)
        print(data)

        time.sleep(rate)
        if total_time >= duration:
            break

def send_csv_data(send_data_func, csv_path, jump, immitate_teensy=False, speedup=1):
    """ Replays a ride recorded to a csv located at csv_path. Starts from [jump] seconds
        Some fields are filled in by DAS.js, so if data will go through DAS.js (i.e. serial_test.py)
        we don't want to send that data """
    with open(csv_path) as csv_data:
        reader = csv.DictReader(csv_data)

        prev_time = 0
        line_count = 0

        for line in reader:
            line_count += 1
            # When speeding up, reduce rows processed to keep the amount of messages roughly the same
            if math.floor(line_count % speedup) != 0:
                continue
            # This datapoint is used a lot so let's store it
            row_time = int(line["time"])

            # Skip to specified time
            if row_time / 1000 < jump:
                prev_time = row_time
                continue

            # Pause for the time elapsed according to the csv
            time.sleep((row_time - prev_time) / 1000 / speedup)
            prev_time = row_time

            # Create data to send via MQTT
            data = "&gps={}&gps_course={}&gps_speed={}&gps_satellites={}" \
                    .format(line["gps"], line["gps_course"], line["gps_speed"], line["gps_satellites"])
            data += "&aX={}&aY={}&aZ={}".format(line["aX"], line["aY"], line["aZ"])
            data += "&gX={}&gY={}&gZ={}".format(line["gX"], line["gY"], line["gZ"])
            data += "&thermoC={}&thermoF={}".format(line["thermoC"], line["thermoF"])
            data += "&pot={}".format(line["pot"])
            data += "&reed_velocity={}&reed_distance={}".format(line["reed_velocity"], line["reed_distance"])

            if not immitate_teensy:
                data += "&filename={}".format(os.path.basename(csv_path))
                data += "time={}".format(row_time)
                data += "&power={}&cadence={}".format(line["power"], line["cadence"])

            # Mid July 2019 - field gps_location split into three separate columns
            if "gps_location" in reader.fieldnames:
                [gps_lat, gps_long, gps_alt] = line["gps_location"].split(",")
            else:
                gps_lat, gps_long, gps_alt = line["gps_lat"], line["gps_long"], line["gps_alt"]
            data += "&gps_lat={}&gps_long={}&gps_alt={}".format(gps_lat, gps_long, gps_alt)

            send_data_func(data)
            print(data)

        print("End of csv, exiting...")
