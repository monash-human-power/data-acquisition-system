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
    # TODO: ADD THE CORRECT '/'

    # Subscribe to all of the data topics
    client.subscribe("v3/wireless-sensor/1/data")
    client.subscribe("v3/wireless-sensor/2/data")
    client.subscribe("v3/wireless-sensor/3/data")

    # Subscribe to all of the battery topics
    client.subscribe("v3/wireless-sensor/battery/low")
    client.subscribe("v3/wireless-sensor/1/battery")
    client.subscribe("v3/wireless-sensor/2/battery")
    client.subscribe("v3/wireless-sensor/3/battery")

    # Subscribe to all of the start topics
    client.subscribe("v3/wireless-module/1/start")
    client.subscribe("v3/wireless-module/2/start")
    client.subscribe("v3/wireless-module/3/start")

    # Subscribe to all of the stop topics
    client.subscribe("v3/wireless-module/1/stop")
    client.subscribe("v3/wireless-module/2/stop")
    client.subscribe("v3/wireless-module/3/stop")


def on_message(client, userdata, msg):
    # TODO: FIX THE TOPICS TO SPEC
    # TODO: ADD THE CORRECT '/'
    module_id = str("M" + msg.topic[19])
    if msg.topic[:18] == "v3/wireless-module" and msg.topic[-5:] == "start":
        is_recording[module_id] = True

    elif msg.topic[:18] == "v3/wireless-module" and msg.topic[-4:] == "stop":
        is_recording[module_id] = False

    else:
        if is_recording[module_id] is True:
            DataToTempCSV(msg, module_id)


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
    is_recording = {
        "M1": False,
        "M2": False,
        "M3": False,
    }

    broker_address = 'localhost'
    client = mqtt.Client()

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(broker_address)

    client.loop_forever()
