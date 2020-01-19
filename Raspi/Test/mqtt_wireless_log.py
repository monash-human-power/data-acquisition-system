import argparse
import paho.mqtt.client as mqtt
import os
import pandas as pd
from DataToTempCSV import DataToTempCSV
import json

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
    if msg.topic.endswith("start"):
        # Decode the data as utf-8 and load into python dict
        start_data = msg.payload.decode("utf-8")
        start_data = json.loads(start_data)

        # Update is_recording dict with correct filename and status
        is_recording[module_id] = True
        is_recording[module_id + "_filename"] = start_data["filename"]
        print(module_id, "STARTED")

        # mosquitto_pub -h localhost -t v3/wireless-module/1/start -m '{"filename": "blk1.csv"}'
        # mosquitto_pub -h localhost -t v3/wireless-module/1/stop -m ''
        # mosquitto_pub -h localhost -t v3/wireless-sensor/battery/low -m '{"module-id": 1}'

    elif msg.topic.endswith("stop"):
        # Update is_recording to stop the recording of the wireless module
        is_recording[module_id] = False
        print(module_id, "STOPPED")

        # Save the temporary data into CSV with the name denoted by the filename
        save_temp_csv(module_id)
        print(module_id, "SAVED")

    else:
        if msg.topic == "v3/wireless-sensor/battery/low":
            DataToTempCSV(msg)
        elif is_recording[module_id] is True:
            DataToTempCSV(msg, module_id)


def save_temp_csv(module_id):
    filename = is_recording[module_id + "_filename"]
    x = find_temp_csvs(module_id)

    print(filename)
    print(x)




def find_temp_csvs(module_id=""):
    """Searches throught the current directory and finds all the temp files and
    merges them it finds a """
    current_dir = os.path.dirname(__file__)
    filenames = os.listdir(current_dir)

    temp_filenames = []

    for filename in filenames:
        # Find the temp files and store in the array
        if filename.startswith(".~temp_" + module_id) and filename.endswith(".csv"):
            temp_filenames.append(current_dir + '/' + filename)

    return temp_filenames
    # merge_temps_pandas(output_filename, temp_filenames)


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
        "M1_filename": None,
        "M2_filename": None,
        "M2_filename": None,
    }

    broker_address = 'localhost'
    client = mqtt.Client()

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(broker_address)

    client.loop_forever()
