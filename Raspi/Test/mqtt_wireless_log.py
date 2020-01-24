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

        # Save the state of recording and the output filename to global dicts
        is_recording[module_id] = True
        output_filename[module_id] = start_data["filename"]

        print(module_id, "STARTED")

    # Stop the recording of <module_id>
    elif msg.topic.endswith("stop"):
        # Change the state of recording to false in global dict
        is_recording[module_id] = False

        print(module_id, "STOPPED")

        # Save the temp CSV data into a proper CSV
        save_temp_csv(module_id)

    # Record low battery data
    elif msg.topic == "/v3/wireless-module/battery/low":
        DataToTempCSV(msg)

    # Record other data
    elif is_recording[module_id] is True:
        DataToTempCSV(msg, module_id)


def save_temp_csv(module_id):
    """ Saves the temp csvs into real csvs where the battery data and the
    module data is combined into a single CSV"""

    # Find the temp files in the current folder for the current module
    temp_filepaths = find_temp_csvs(module_id)

    # Merge the battery and sensor data into a single CSV
    merge_temps(output_filename[module_id], temp_filepaths)

    # Remove the temp files for the specific module that where generated
    remove_files(temp_filepaths)


def find_temp_csvs(module_id=""):
    """ Searches throught the current directory and finds all the temp files
    for a specific module_id and returns the filepaths in a list. If no
    module_id is given then all temporary files will be found and returned
    in a list."""

    current_dir = os.path.dirname(__file__)

    # Depends on where the python script is called from
    if current_dir == '':
        filepaths = os.listdir()
    else:
        filepaths = os.listdir(current_dir)

    # Find temp filepaths and store in the temp_filepaths list
    temp_filepaths = []
    for filename in filepaths:
        if filename.startswith(".~temp_" + module_id) and filename.endswith(".csv"):
            if current_dir == '':
                temp_filepaths.append(filename)
            else:
                temp_filepaths.append(current_dir + '/' + filename)

    return temp_filepaths


def remove_files(filepaths):
    """ Removes the files in a list of filepaths
    filepaths: Example list of filepaths is [filepath1, filepath2, filepath3]
    """
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

    # M1, M1_filename
    is_recording = {}
    output_filename = {}

    broker_address = 'localhost'
    client = mqtt.Client()

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(broker_address)

    client.loop_forever()
