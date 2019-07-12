import sys
import time
import random
import argparse
import csv
import paho.mqtt.client as mqtt

# Arguments
parser = argparse.ArgumentParser(description='DAS MQTT python script', add_help=True)
parser.add_argument('-t', '--time', action='store', type=int, default=1, help="length of time to send data")
parser.add_argument('-r', '--rate', action='store', type=float, default=0.5, help="rate of data in seconds")
parser.add_argument('--host', action='store', type=str, default="localhost", help="address of the MQTT broker")
parser.add_argument('-f', '--file', action='store', type=str, help="The csv file to replay. If not specified, makes up data.")
parser.add_argument('-j', '--jump', action='store', type=int, default=0, help="Starts replaying from a specified time (in seconds)")

def send_fake_data(client, duration, rate):
    """ Send artificial data over MQTT if no file is specified. Sends [rate] per second for [duration] seconds """
    start_time = round(time.time(), 2)
    gps_speed = 0
    while True:
        current_time = round(time.time(), 2)
        total_time = round(current_time - start_time, 2)

        # Generate data message
        data = "gps=1&gps_lat=00&gps_long=00&gps_alt=00&gps_course=00&"
        gps_speed = random.random() * (total_time) + gps_speed
        data += "gps_speed=" + str(gps_speed)
        data += "&gps_satellites=00"
        data += "&aX=00.0000&aY=00.0000&aZ=00.0000&gX=00.0000&"
        data += "gY=00.0000&gZ=00.0000"
        data += "&thermoC=25.00&thermoF=25.00"
        data += "&pot=100"
        data += "&filename=test.csv"
        data += "&time=" + str(total_time * 1000)
        data += "&power=" + str(random.randint(0, 150))
        data += "&cadence=" + str(random.randint(0, 150))
        data += "&reed_velocity=" + str(random.randint(0, 150))
        data += "&reed_distance=" + str(random.randint(0, 150))

        client.publish("data", data)
        print(data)

        time.sleep(rate)
        if total_time >= duration:
            break

def send_csv_data(client, csv_path, jump):
    """ Replays a ride recorded to a csv located at csv_path. Starts from [jump] seconds """
    with open(csv_path) as csv_data:
        reader = csv.DictReader(csv_data)

        prev_time = 0

        for line in reader:
            # This datapoint is used a lot so let's store it
            row_time = int(line["time"])

            # Skip to specified time
            if row_time / 1000 < jump:
                prev_time = row_time
                continue

            # Pause for the time elapsed according to the csv
            time.sleep((row_time - prev_time) / 1000)
            prev_time = row_time

            # Create data to send via MQTT
            data = "time={}".format(row_time)
            data += "&gps={}&gps_course={}&gps_speed={}&gps_satellites={}" \
                    .format(line["gps"], line["gps_course"], line["gps_speed"], line["gps_satellites"])
            data += "&aX={}&aY={}&aZ={}".format(line["aX"], line["aY"], line["aZ"])
            data += "&gX={}&gY={}&gZ={}".format(line["gX"], line["gY"], line["gZ"])
            data += "&thermoC={}&thermoF={}".format(line["thermoC"], line["thermoF"])
            data += "&pot={}".format(line["pot"])
            data += "&power={}&cadence={}".format(line["power"], line["cadence"])
            data += "&reed_velocity={}&reed_distance={}".format(line["reed_velocity"], line["reed_distance"])

            # Mid July 2019 - field gps_location split into three separate columns
            if "gps_location" in reader.fieldnames:
                [gps_lat, gps_long, gps_alt] = line["gps_location"].split(",")
            else:
                gps_lat, gps_long, gps_alt = line["gps_lat"], line["gps_long"], line["gps_alt"]
            data += "&gps_lat={}&gps_long={}&gps_alt={}".format(gps_lat, gps_long, gps_alt)

            print(data)
            client.publish("data", data)

def start_publishing(client, args):
    print("start")
    client.publish("power_model/start")
    client.publish("start")

    if args.file is None:
        send_fake_data(client, args.time, args.rate)
    else:
        send_csv_data(client, args.file, args.jump)

    print("stop")
    client.publish("stop")
    client.publish("power_model/stop")
    sys.exit(0)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload.decode("utf-8")))

def run():
    args = parser.parse_args()
    broker_address = args.host
    client = mqtt.Client()

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(broker_address)
    start_publishing(client, args)

    client.loop_forever()

run()
