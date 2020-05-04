import json
from datetime import datetime
import os
import csv
import Raspi.utils.enum_topics


def DataToTempCSV(msg, module_start_time, module_id_str, module_id_num):
    """ Function to parse the MQTT data and convert it to a temporary
    CSV file stored in the current derectory
    msg:                        Raw MQTT data
    module_id_str:              Module_id eg. M1, M2 or M3
    module_start_time:          Start time of the module (datetime obj)
    """

    def parse_module_data():
        """ Parses the module data if it is from the sensors """

        # Retrieve sensor data from python dict
        sensor_data = module_data["sensors"]

        for sensor in sensor_data:
            sensor_name = module_id_str + "_" + sensor["type"]
            sensor_value = sensor["value"]

            if isinstance(sensor_value, dict):
                # For nested sensor values
                for (sub_sensor, sub_sensor_value) in sensor_value.items():
                    sub_sensor_name = sensor_name + '_' + sub_sensor
                    data_dict[sub_sensor_name] = sub_sensor_value
            else:
                data_dict[sensor_name] = sensor_value

    def parse_module_battery():
        """ Parses the module data if it is from the battery """

        data_dict[module_id_str + "_percentage"] = \
            module_data["percentage"]

    def make_temp_csv():
        """ Makes a temporary CSV file that is hidden and is in the form of
        .~temp_<filename>.csv in the current directory"""

        # Ensures that the temp file is in the same folder as the script
        current_dir = os.path.dirname(__file__)
        temp_filename = '.~temp_' + module_id_str + '_' + type + '.csv'
        temp_file_path = os.path.join(current_dir, temp_filename)

        # If the temp file does not exist write the headers for the CSV
        temp_exists = os.path.exists(temp_file_path)

        with open(temp_file_path, mode='a') as temp_file:
            csv_writer = csv.DictWriter(
                temp_file,
                fieldnames=data_dict.keys())

            if not temp_exists:
                csv_writer.writeheader()

            # Append the data onto the temporary file
            csv_writer.writerow(data_dict)

    data_dict = {}  # Data to be output to a temp CSV

    # Decode the data as utf-8 and load into python dict
    module_data = msg.payload.decode("utf-8")
    module_data = json.loads(module_data)

    # Determine which type of data to parse
    if enum_topics.WirelessModule.data(module_id_num) == msg.topic:
        type = str(enum_topics.WirelessModuleType.data)
        parse_module_data()

    elif enum_topics.WirelessModule.low_battery(module_id_num) == msg.topic:
        type = str(enum_topics.WirelessModuleType.low_battery)
        # Nothing to parse

    elif enum_topics.WirelessModule.battery(module_id_num) == msg.topic:
        type = str(enum_topics.WirelessModuleType.battery)
        parse_module_battery()

    # Find the difference in seconds to when the recording was started and
    # when the data was recieved.
    time_delta = datetime.now() - module_start_time
    time_delta = time_delta.total_seconds()
    time_dict_key = f"{module_id_str}_{type}_TIME"
    data_dict[time_dict_key] = time_delta

    # Add or create the temp CSV to store the data
    make_temp_csv()
