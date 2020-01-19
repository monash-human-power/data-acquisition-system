import csv
import json
import argparse
import paho.mqtt.client as mqtt
import os
from datetime import datetime
import pandas as pd
from DataToTempCSV import DataToTempCSV

"""
FIX THE "wireless-sensor" --> "wireless-module"

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

    subscribe_to_all(client)


def subscribe_to_all(client):
    # TODO: FIX THE TOPICS TO SPEC

    # Subscribe to all of the data topics
    client.subscribe("v3/wireless-sensor/1/data")
    client.subscribe("v3/wireless-sensor/2/data")
    client.subscribe("v3/wireless-sensor/3/data")

    # Subscribe to all of the battery topics
    client.subscribe("v3/wireless-sensor/battery/low")
    client.subscribe("v3/wireless-sensor/1/battery")
    client.subscribe("v3/wireless-sensor/2/battery")
    client.subscribe("v3/wireless-sensor/3/battery")


def on_message(client, userdata, msg):
    # TODO: FIX THE TOPICS TO SPEC

    # Capture the data and decode the JSON

    # IMPLEMENT A FUNCTION FOR THIS
    # /v3/wireless-module/<id>/start
    # /v3/wireless-module/<id>/stop

    # Check to see if the topic ends in "data", selecting only the msg's that
    # have wireless_module_data
    # if msg.topic[:18] == "v3/wireless-sensor" and msg.topic[-4:] == "data":
    #     data_dict = parse_wireless_module_data(msg)
    #     temp_csv(msg, data_dict)
    #     print(msg.payload.decode("utf-8"))

    DataToTempCSV(msg)

def merge_temps(output_filename):
    """Searches throught the current directory and finds all the temp files and
    merges them it finds a """
    current_dir = os.path.dirname(__file__)
    filenames = os.listdir(current_dir)
    output_filename = current_dir + '/' + output_filename

    temp_filenames = []

    for filename in filenames:
        # Find the temp files and store in the array
        if filename[-4:] == ".csv" and filename[:6] == ".~temp":
            temp_filenames.append(current_dir + '/' + filename)

    merge_temps_pandas(output_filename, temp_filenames)


def merge_temps_pandas(output_filename, temp_filenames):
    df_array = []
    df_columns = []
    dataframe = pd.DataFrame()
    for temp_filename in temp_filenames:

        temp = pd.read_csv(temp_filename)
        for column in temp.columns:
            print('-->',str(column))
            dataframe[str(column)] = temp[column]

    dataframe.to_csv(output_filename)


def parse_wireless_module_data(msg):
    module_data = msg.payload.decode("utf-8")   # Decode the data as utf-8
    module_data = json.loads(module_data)       # Load from json to dict
    sensor_data = module_data["sensors"]        # Retrieve sensor data
    module_id = str("M" + msg.topic[19])        # Find module ID

    # Used to store the data before being entered into the csv
    data_dict = {}

    for sensor in sensor_data:
        sensor_type = module_id + "_" + sensor["type"]
        sensor_value = sensor["value"]

        if isinstance(sensor_value, dict):
            pass
        else:
            data_dict[sensor_type] = sensor_value

    # Add in the time and date that the data came in
    data_dict[module_id + "_time"] = str(datetime.now().time())
    return data_dict


def temp_csv(msg, data_dict):
    # make sure that the temp file is
    current_dir = os.path.dirname(__file__)
    temp_filename = msg.topic.replace('/', '-')
    temp_file_path = os.path.join(current_dir, str('.~temp_' + temp_filename + '.csv'))

    fieldnames = []
    for key in data_dict.keys():
        fieldnames.append(key)

    # print(temp_file_path)
    if not os.path.exists(temp_file_path):
        # If the temp file does not exist write the headers for the CSV
        with open(temp_file_path, mode='a') as temp_file:
            csv_writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
            csv_writer.writeheader()

    with open(temp_file_path, mode='a') as temp_file:
        csv_writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
        csv_writer.writerow(data_dict)


if __name__ == "__main__":
    broker_address = 'localhost'
    client = mqtt.Client()

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(broker_address)

    client.loop_forever()
