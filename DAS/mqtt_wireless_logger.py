import paho.mqtt.client as mqtt
import os
import pandas as pd
from datetime import datetime
import argparse
import glob
import re
from DAS.utils.DataToTempCSV import DataToTempCSV 
from DAS.utils import enum_topics 


# Global dicts to store state
# Dict structure is {<module_id_str> : <data>}
is_recording = {}       # If the data is being recorded
module_start_time = {}  # When the data started being recorded
# output_filename = {}    # Output filename
output_filepath = {}    # Output filpath to save the file

# Global file path
GLOBAL_FILEPATH = os.path.dirname(__file__)

# Global names
TEMP_DIR = os.path.join(GLOBAL_FILEPATH, ".~temps")
CSV_DIR = os.path.join(GLOBAL_FILEPATH, "csv_data")

parser = argparse.ArgumentParser(
    description='MQTT wireless logger',
    add_help=True)

parser.add_argument(
    '--host', action='store', type=str, default="localhost",
    help="""Address of the MQTT broker. If nothing is selected it will
    default to localhost.""")


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
    '/v3/wireless-module/#' topics. The module_id_str is found by squashing M
    infront of the module number. eg M1, M2, M3... etc. The module_id_str is
    used for identifying what data came from where and is also used for naming
    the temp files.
    """
    module_id_num = msg.topic.split("/")[3]
    module_id_str = "M" + module_id_num

    # Start the recording of <module_id>
    if enum_topics.WirelessModule.start(module_id_num) == msg.topic:
        start_recording(module_id_str)
        print(module_id_str,
              "STARTED, RECORDING TO FILE:",
              output_filepath[module_id_str])

    # Stop the recording of <module_id>
    elif enum_topics.WirelessModule.stop(module_id_num) == msg.topic:
        stop_recording(module_id_str)
        print(module_id_str,
              "STOPPED, RECORDED TO FILE:",
              output_filepath[module_id_str])

    # Record data (battery, low-battery and sensor data)
    elif is_recording[module_id_str]:
        DataToTempCSV(
            msg, module_start_time[module_id_str],
            module_id_str, module_id_num, TEMP_DIR)


def start_recording(module_id_str):
    """ Start recording for a specific module """
    # Save the state of recording and the output filename to global dicts
    is_recording[module_id_str] = True
    module_start_time[module_id_str] = datetime.now()

    # Generate filename from the last log number + 1
    max_file_id = 0
    for filepath in glob.glob(os.path.join(CSV_DIR,'*_M?.csv')):
        # split the filepath into the filename
        filename = filepath.split("/")[-1]

        # Gets all the digits from the file name
        temp = re.findall(r'\d+', filename)

        # Gets all the digits from the file name
        file_id = list(map(int, temp))[0]

        if file_id > max_file_id:
            max_file_id = file_id

    # Save output filepath in global dict
    output_filename = f"{max_file_id+1}_{module_id_str}.csv"
    print(output_filename)
    output_filepath[module_id_str] = os.path.join(CSV_DIR, output_filename)


def stop_recording(module_id_str):
    """ Stop recording for a specific module """
    # Change the state of recording to false in global dict
    is_recording[module_id_str] = False

    # Find the temp files in the current folder for the current module
    temp_filepaths = find_temp_csvs(module_id_str)

    # Merge the battery and sensor data into a single CSV
    merge_and_save_temps(temp_filepaths, output_filepath[module_id_str])

    # Remove the temp files for the specific module that where generated
    for file in temp_filepaths:
        os.remove(file)


def find_temp_csvs(module_id_str=""):
    """ Searches throught the current directory and finds all the temp files
    for a specific module_id_str and returns the filepaths in a list. If no
    module_id_str is given then all temporary files will be found and returned
    in a list."""
    
    # Find temp filepaths and store in the temp_filepaths list
    temp_filepaths = []
    for filename in os.listdir(TEMP_DIR):
        if filename.startswith(f".~temp_{module_id_str}_") and filename.endswith(".csv"):
            temp_filepaths.append(os.path.join(TEMP_DIR, filename))
        
    return temp_filepaths


def merge_and_save_temps(temp_filepaths, save_filepath):
    """ This function merges multiple temporary module CSVs into a final one
    and names the file correctly.
    temp_filepaths:     Example list of filepaths is [filepath1, filepath2]"""

    # Place all of the pandas dataframes into a list
    temp_dataframes = []
    for temp_filename in temp_filepaths:
        df = pd.read_csv(temp_filename)
        temp_dataframes.append(df)
    
    # Merge the dataframes and output the final csv
    try:
        merged_dataframe = pd.concat(temp_dataframes, axis=1)
    except Exception as e:
        print(e)

    merged_dataframe.to_csv(save_filepath)

if __name__ == "__main__":
    args = parser.parse_args()
    broker_address = args.host
    client = mqtt.Client()

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(broker_address)

    client.loop_forever()
