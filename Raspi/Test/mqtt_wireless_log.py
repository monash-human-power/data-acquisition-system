import argparse
import paho.mqtt.client as mqtt
import os
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
    # IMPLEMENT A FUNCTION FOR THIS
    # /v3/wireless-module/<id>/start
    # /v3/wireless-module/<id>/stop
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


if __name__ == "__main__":
    broker_address = 'localhost'
    client = mqtt.Client()

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(broker_address)

    client.loop_forever()
