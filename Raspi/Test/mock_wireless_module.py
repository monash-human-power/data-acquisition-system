# MQTT wireless sensor test script that sends fake randomly generated data
# To do a single test --> python3 mqtt_wireless_test.py -t 0

import sys
import time
import random
import argparse
import json
import paho.mqtt.client as mqtt

class Sensors:

    decimals = 2            # number of decimal places for the random generated val
    percentRange = 0.05     # percent range for the rangomly generated value

    def CO2(val=325):
        # value in ppm (normal background conentration 250-400ppm)
        return round(val + val*random.uniform(-Sensors.percentRange, Sensors.percentRange), Sensors.decimals)

    def humidity(val=75):
        # value as a percentage of humidity
        return round(val + val*random.uniform(-Sensors.percentRange, Sensors.percentRange), Sensors.decimals)

    def temperature(val=20):
        # value in degrees celcius
        return round(val + val*random.uniform(-Sensors.percentRange, Sensors.percentRange), Sensors.decimals)

    def accelerometer(val=5):
        # value in m/s^2 for all axis stored in a dictionary
        return {
        "x": round(val + val*random.uniform(-Sensors.percentRange, Sensors.percentRange), Sensors.decimals),
        "y": round(val + val*random.uniform(-Sensors.percentRange, Sensors.percentRange), Sensors.decimals),
        "z": round(val + val*random.uniform(-Sensors.percentRange, Sensors.percentRange), Sensors.decimals)}

    def gyroscope(val=90):
        # value in degrees for all axis stored in a dictionary
        return {
        "x": round(val + val*random.uniform(-Sensors.percentRange, Sensors.percentRange), Sensors.decimals),
        "y": round(val + val*random.uniform(-Sensors.percentRange, Sensors.percentRange), Sensors.decimals),
        "z": round(val + val*random.uniform(-Sensors.percentRange, Sensors.percentRange), Sensors.decimals)}

    def battery(val=80):
        # value as a percentage of the battery
        return round(val + val*random.uniform(-Sensors.percentRange, Sensors.percentRange), Sensors.decimals)

    def reedSwitch(val=True):
        # value as either true or false
        return val

    def GPS(latLngVal=20, speedVal=50):
        # returns the latatude, longatude and the GPS speed of the bike stored in a dictionary
        return {
        "lat": round(latLngVal + latLngVal*random.uniform(-Sensors.percentRange, Sensors.percentRange), Sensors.decimals),
        "lng": round(latLngVal + latLngVal*random.uniform(-Sensors.percentRange, Sensors.percentRange), Sensors.decimals),
        "speed": round(speedVal + speedVal*random.uniform(-Sensors.percentRange, Sensors.percentRange), Sensors.decimals)}

    def steering(val=0):
        # value in degrees for the position of the steering stem
        return round(val + random.uniform(-90, 90), Sensors.decimals)\

    def time():
        # return the current time for the sensor as Unix Epoch time
        return time.time()

parser = argparse.ArgumentParser(description='MQTT wireless sensor test script that sends fake data', add_help=True)
parser.add_argument('-t', '--time', action='store', type=int, default=float('Inf'), help="Length of time to send data in seconds (duration). If nothing is selected it will continuously send out data.")
parser.add_argument('-r', '--rate', action='store', type=float, default=1, help="Rate of data in data sent per second. Default is 1 data pack sent per second.")
parser.add_argument('--host', action='store', type=str, default="192.168.100.100", help="Address of the MQTT broker. If nothing is selected it will default to 192.168.100.100.")
parser.add_argument('--id', action='store', type=int, default=None, help="Specify the sensor to produce fake data. eg. --id 1 specifies that sensor 1 only produces data. If nothing is given all sensors will be active." )

def send_fake_data(client, duration, rate, sensorID):
    """ Send artificial data over MQTT for each sensor chanel. Sends [rate] per second for [duration] seconds """

    start_time = round(time.time(), 2)

    while True:
        current_time = round(time.time(), 2)
        total_time = round(current_time - start_time, 2)

        print() # Newline for clarity

        # Wireless Sensor 1 (Middle)
        if sensorID == 1 or sensorID == None:

            # generate JSON data and publish it over MQTT
            data = {
                "CO2": Sensors.CO2(),
                "temperature": Sensors.temperature(),
                "humidity": Sensors.humidity(),
                "accelerometer": Sensors.accelerometer(),
                "gyroscope": Sensors.gyroscope(),
                "battery": Sensors.battery(),
                "time": Sensors.time()}

            JSON_data = json.dumps(data)
            pub_path = "v3/wireless-sensor/1/data"

            client.publish(pub_path, JSON_data)
            print(pub_path, "--> ", JSON_data)

        # Wireless Sensor 2 (client, Back)
        if sensorID == 2 or sensorID == None:

            # generate JSON data and publish it over MQTT
            data = {
                "CO2": Sensors.CO2(),
                "reedSwitch": Sensors.reedSwitch(),
                "GPS": Sensors.GPS(),
                "temperature": Sensors.temperature(),
                "battery": Sensors.battery(),
                "time": Sensors.time()}

            JSON_data = json.dumps(data)
            pub_path = "v3/wireless-sensor/2/data"

            client.publish(pub_path, JSON_data)
            print(pub_path, "--> ", JSON_data)

        # Wireless Sensor 3 (client, Front)
        if sensorID == 3 or sensorID == None:

            # generate JSON data and publish it over MQTT
            data = {
                "steering": Sensors.steering(),
                "temperature": Sensors.temperature(),
                "humidity": Sensors.humidity(),
                "battery": Sensors.battery(),
                "time": Sensors.time()}

            JSON_data = json.dumps(data)
            pub_path = "v3/wireless-sensor/3/data"

            client.publish(pub_path, JSON_data)
            print(pub_path, "--> ", JSON_data)


        time.sleep(1/rate)
        if total_time >= duration:
            break

def start_publishing(client, args):
    print("publishing started...")

    send_fake_data(client, args.time, args.rate, args.id)

    print("publishing finished")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected Sucessfully! Result code: " + str(rc))
    else:
        print("Something went wrong! Result code: " + str(rc))

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload.decode("utf-8")))

def run():
    args = parser.parse_args()
    broker_address = args.host
    client = mqtt.Client()

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(broker_address)
    client.loop_start()
    start_publishing(client, args)
    client.loop_stop()

run()
