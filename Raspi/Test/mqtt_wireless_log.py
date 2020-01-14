import csv
import json
import argparse
import paho.mqtt.client as mqtt
import os
import pandas as pd

"""
1. Subscribe to the chanels
2. Capture and decode the JSON
3. Convert the json to csv
4. append the data to the csv file

# NOTE: The battery will be implemented later. Just do the key data first.

"""


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected Sucessfully! Result code: " + str(rc))

    else:
        print("Something went wrong! Result code: " + str(rc))

    # Subscribe to all of the data topics
    client.subscribe("/v3/wireless-module/1/data")
    client.subscribe("/v3/wireless-module/2/data")
    client.subscribe("/v3/wireless-module/3/data")

    # Subscribe to all of the battery topics
    client.subscribe("/v3/wireless-module/battery/low")
    client.subscribe("/v3/wireless-module/1/battery")
    client.subscribe("/v3/wireless-module/2/battery")
    client.subscribe("/v3/wireless-module/3/battery")


def on_message(client, userdata, msg):
    # Capture the data and decode the JSON

    # IMPLEMENT A FUNCTION FOR THIS
    # /v3/wireless-module/<id>/start
    # /v3/wireless-module/<id>/stop

    # Check to see if the topic ends in "data", selecting only the msg's that
    # have wireless_module_data
    if msg.topic[:19] == "/v3/wireless-module" and msg.topic[-4:] == "data":
        parse_wireless_module_data(msg)


def parse_wireless_module_data(msg):
    module_data = msg.payload.decode("utf-8")
    module_data = json.loads(module_data)
    sensor_data = module_data["sensors"]
    for sensor in sensor_data:
        sensor_type = sensor["type"]
        sensor_value = sensor["value"]



        # with open(filename, mode='a') as csv_file:
        #
        #     fieldnames = ['co2', 'temperature', 'humidity', 'accelerometer', 'gyroscope']
        #     writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        #
        #     writer.writeheader()
        #     writer.writerow({sensor_type: sensor_value})
        #     # writer.writerow({'dept': 'IT', 'birth_month': 'March', 'emp_name': 'Erica Meyers'})



    # print(sensor_data)
    # print(module_data)


if __name__ == "__main__":
    # GO WITH 3 CSVs
    # TODO: REMOVE THIS FOR CLI VERSION
    dir = os.path.dirname(__file__)
    filename = os.path.join(dir, 'mqtt_wireless_log.csv')
    print(filename)

    df = pd.read_csv(filename)
    print(df.iloc[-1]['temperature'])
    df.iloc[-1]['temperature'] = 1
    print(df.iloc[-1]['temperature'])

    # print(df.loc(0, 'temperature'))

    broker_address = 'localhost'
    client = mqtt.Client()

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(broker_address)

    client.loop_forever()
