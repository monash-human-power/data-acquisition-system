import csv
import json
import argparse
import paho.mqtt.client as mqtt
import os

"""
# USE 3 TEMP CSV and then merge at the end

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


def temp_csv(data_name, data_dict):
    # make sure that the temp file is
    current_dir = os.path.dirname(__file__)
    temp_file_path = os.path.join(current_dir, str('.~temp_' + data_name + '.csv'))

    print(type(data_dict.keys()))
    fieldnames = []
    for key in data_dict.keys():
        fieldnames.append(key)
    print(temp_file_path)

    if not os.path.exists(temp_file_path):
        # If the temp file does not exist write the headers for the CSV
        with open(temp_file_path, mode='a') as temp_file:
            csv_writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
            csv_writer.writeheader()

    with open(temp_file_path, mode='a') as temp_file:
        csv_writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
        csv_writer.writerow(data_dict)
        # csv_writer.writerow(['Erica Meyers', 'IT', 'March'])


if __name__ == "__main__":

    temp_csv("sensor1", {'data_dict': 3, 'yoyoy': 'helloworld'})

    # # GO WITH 3 CSVs
    # # TODO: REMOVE THIS FOR CLI VERSION
    #
    # broker_address = 'localhost'
    # client = mqtt.Client()
    #
    # client.on_connect = on_connect
    # client.on_message = on_message
    #
    # client.connect(broker_address)
    #
    # client.loop_forever()
