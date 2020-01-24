import argparse
import paho.mqtt.client as mqtt
import os
import pandas as pd
from DataToTempCSV import DataToTempCSV
import json


def on_connect(client, userdata, flags, rc):
    """ When the MQTT client connects to the broker it prints out if it
    connects successfully and then subscribes to all of the wireless-module
    topics"""

    if rc == 0:
        print("Connected Successfully! Result code: " + str(rc))
    else:
        print("Something went wrong! Result code: " + str(rc))

    # Subscribe to all of the wireless module topics
    client.subscribe("/v3/wireless-module/#")


def on_message(client, userdata, msg):
    """ MQTT callback for when data is sent on the subscribed
    '/v3/wireless-module/#' topics. The module_id is found by squashing M
    infront of the module number. eg M1, M2, M3... etc. The module_id is used
    for identifying what data came from where and is also used for naming the
    temp files.
    """

    module_id = "M" + str(msg.topic[20])

    # Start the recording of <module_id>
    if msg.topic.endswith("start"):
        start_data = msg.payload.decode("utf-8")
        start_data = json.loads(start_data)

        # Set the module to recording in the 'is_recording' dict
        is_recording[module_id] = True
        # ######Set the module to recording in the 'is_recording' dict
        output_filename[module_id] = start_data["filename"]

        print(module_id, "STARTED")

    # Stop the recording of <module_id>
    elif msg.topic.endswith("stop"):
        # Update is_recording to stop the recording of the wireless module
        is_recording[module_id] = False
        print(module_id, "STOPPED")

        # Save the temporary data into a perminent CSV
        save_temp_csv(module_id)

    else:
        # low battery
        if msg.topic == "/v3/wireless-module/battery/low":
            DataToTempCSV(msg)
        # low battery just record normal data
        elif is_recording[module_id] is True:
            DataToTempCSV(msg, module_id)


def save_temp_csv(module_id):
    temp_filepaths = find_temp_csvs(module_id)
    merge_temps(output_filename[module_id], temp_filepaths)
    remove_files(temp_filepaths)


def find_temp_csvs(module_id=""):
    """Searches throught the current directory and finds all the temp files and
    merges them it finds a """
    current_dir = os.path.dirname(__file__)

    if current_dir == '':
        filepaths = os.listdir()
    else:
        filepaths = os.listdir(current_dir)

    temp_filepaths = []
    for filename in filepaths:
        # Find the temp filepaths and store in the array
        if filename.startswith(".~temp_" + module_id) and filename.endswith(".csv"):
            if current_dir == '':
                temp_filepaths.append(filename)
            else:
                temp_filepaths.append(current_dir + '/' + filename)

    return temp_filepaths


def remove_files(filepaths):
    """ Removes the files in the list of filepaths """
    for file in filepaths:
        os.remove(file)


def merge_temps(output_filename, temp_filepaths):
    temps_dataframes = []
    for temp_filename in temp_filepaths:
        temp_df = pd.read_csv(temp_filename)
        temps_dataframes.append(temp_df)

    merged_dataframe = pd.concat(temps_dataframes, axis=1)

    merged_dataframe.to_csv(output_filename)


if __name__ == "__main__":
    remove_files(find_temp_csvs())

    is_recording = {
        # "M1": False,
        # "M2": False,
        # "M3": False,
        # "M1_filename": None,
        # "M2_filename": None,
        # "M3_filename": None,
    }

    output_filename = {}

    broker_address = 'localhost'
    client = mqtt.Client()

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(broker_address)

    client.loop_forever()
