import json
from datetime import datetime
import os
import csv


class DataToTempCSV:
    def __init__(self, msg, module_id="ALL"):
        self.msg = msg
        self.data_dict = {}
        self.module_id = module_id

        # Decode the data as utf-8 and load into python dict
        self.module_data = self.msg.payload.decode("utf-8")
        self.module_data = json.loads(self.module_data)

        # Determine which data to parse
        if msg.topic.endswith("data"):
            self.type = "DATA"
            self.parse_module_data()

        elif msg.topic.endswith("battery"):
            self.type = "BATTERY"
            self.parse_module_battery()

        elif msg.topic == "/v3/wireless-module/battery/low":
            self.type = "BATTERY_LOW"
            self.parse_low_battery()

        # Add in the time and date that the data came in
        current_time = str(datetime.now().time())
        self.data_dict[self.module_id+"_"+self.type+"_time"] = current_time

        # Add or create the temp CSV to store the data
        self.make_temp_csv()

    def parse_module_data(self):
        # Retrieve sensor data from python dict
        sensor_data = self.module_data["sensors"]

        for sensor in sensor_data:
            sensor_type = self.module_id + "_" + sensor["type"]
            sensor_value = sensor["value"]

            if isinstance(sensor_value, dict):
                for sub_sensor in sensor_value.keys():
                    sub_sensor_type = sensor_type + '_' + sub_sensor
                    sub_sensor_value = sensor_value[sub_sensor]
                    self.data_dict[sub_sensor_type] = sub_sensor_value
            else:
                self.data_dict[sensor_type] = sensor_value

    def parse_module_battery(self):
        self.data_dict[self.module_id + "_percentage"] = self.module_data["percentage"]

    def parse_low_battery(self):
        self.data_dict["lowBattery"] = 1

    def make_temp_csv(self):
        # Ensures that the temp file is in the same folder as the script
        current_dir = os.path.dirname(__file__)
        temp_filename = str('.~temp_' + self.module_id+'_'+self.type + '.csv')
        temp_file_path = os.path.join(current_dir, temp_filename)

        column_names = []
        for key in self.data_dict.keys():
            column_names.append(key)

        # If the temp file does not exist write the headers for the CSV
        new_file = os.path.exists(temp_file_path)

        with open(temp_file_path, mode='a') as temp_file:
            csv_writer = csv.DictWriter(temp_file, fieldnames=column_names)

            if not new_file:
                csv_writer.writeheader()

            # Append the data onto the temporary file
            csv_writer.writerow(self.data_dict)
