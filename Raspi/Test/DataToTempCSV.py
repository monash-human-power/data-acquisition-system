import json
from datetime import datetime
import os
import csv


def DataToTempCSV(msg, module_start_time, module_id):
    """ Function to parse the MQTT data and convert it to a temporary
    CSV file stored in the current derectory
    msg:                        Raw MQTT data
    module_id:                  Module_id eg. M1, M2 or M3
    module_start_time:          Start time of the module (datetime obj)
    """

    data_dict = {}             # Data to be output to a temp CSV

    # Decode the data as utf-8 and load into python dict
    module_data = msg.payload.decode("utf-8")
    module_data = json.loads(module_data)

    # Determine which type of data to parse
    if msg.topic.endswith("data"):
        type = "DATA"
        parse_module_data()

    elif msg.topic.endswith("battery"):
        type = "BATTERY"
        parse_module_battery()

    elif msg.topic == "/v3/wireless-module/battery/low":
        type = "BATTERY_LOW"
        # Nothing to parse

    # Find the difference in seconds to when the recording was started and
    # when the data was recieved.
    time_delta = datetime.now() - module_start_time
    time_delta = time_delta.total_seconds()
    time_dict_key = f"{module_id}_{type}_TIME"
    data_dict[time_dict_key] = time_delta

    # Add or create the temp CSV to store the data
    self.make_temp_csv()

    def parse_module_data(self):
        """ Parses the module data if it is from the sensors """

        # Retrieve sensor data from python dict
        sensor_data = self.module_data["sensors"]

        for sensor in sensor_data:
            sensor_name = self.module_id + "_" + sensor["type"]
            sensor_value = sensor["value"]

            if isinstance(sensor_value, dict):
                # For nested sensor values
                for (sub_sensor, sub_sensor_value) in sensor_value.items():
                    sub_sensor_name = sensor_name + '_' + sub_sensor
                    self.data_dict[sub_sensor_name] = sub_sensor_value
            else:
                self.data_dict[sensor_name] = sensor_value

    def parse_module_battery(self):
        """ Parses the module data if it is from the battery """

        self.data_dict[self.module_id + "_percentage"] = \
            self.module_data["percentage"]

    def make_temp_csv(self):
        """ Makes a temporary CSV file that is hidden and is in the form of
        .~temp_<filename>.csv in the current directory"""

        # Ensures that the temp file is in the same folder as the script
        current_dir = os.path.dirname(__file__)
        temp_filename = '.~temp_' + self.module_id + '_' + self.type + '.csv'
        temp_file_path = os.path.join(current_dir, temp_filename)

        # If the temp file does not exist write the headers for the CSV
        new_file = os.path.exists(temp_file_path)

        with open(temp_file_path, mode='a') as temp_file:
            csv_writer = csv.DictWriter(
                temp_file,
                fieldnames=self.data_dict.keys())

            if not new_file:
                csv_writer.writeheader()

            # Append the data onto the temporary file
            csv_writer.writerow(self.data_dict)
