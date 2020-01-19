import json
from datetime import datetime
import os
import csv


class DataToTempCSV:
    def __init__(self, msg, module_id):
        # TODO: FIX THE TOPICS TO SPEC
        # TODO: ADD THE CORRECT '/'

        self.msg = msg
        self.data_dict = {}
        self.module_id = module_id

        if msg.topic[:18] == "v3/wireless-sensor" and msg.topic[-4:] == "data":
            self.parse_module_data()

        if msg.topic[:18] == "v3/wireless-sensor" and msg.topic[-7:] == "battery":
            self.parse_module_battery()

        if msg.topic == "v3/wireless-sensor/battery/low":
            self.parse_low_battery()

        self.make_temp_csv()

    def parse_module_data(self):
        # Decode the data as utf-8 and load into python dict
        module_data = self.msg.payload.decode("utf-8")
        module_data = json.loads(module_data)
        # Retrieve sensor data from python dict
        sensor_data = module_data["sensors"]
        # Find module ID
        module_id = str("M" + self.msg.topic[19])

        for sensor in sensor_data:
            sensor_type = module_id + "_" + sensor["type"]
            sensor_value = sensor["value"]

            if isinstance(sensor_value, dict):
                for sub_sensor in sensor_value.keys():
                    sub_sensor_type = sensor_type + '_' + sub_sensor
                    sub_sensor_value = sensor_value[sub_sensor]
                    self.data_dict[sub_sensor_type] = sub_sensor_value

            else:
                self.data_dict[sensor_type] = sensor_value

        # Add in the time and date that the data came in
        self.data_dict[module_id + "_time"] = str(datetime.now().time())

    def parse_module_battery(self):
        # Decode the data as utf-8 and load into python dict
        module_data = self.msg.payload.decode("utf-8")
        module_data = json.loads(module_data)
        # Retrieve module data from python dict
        module_id = "M" + module_data["module-id"]

        self.data_dict[module_id + "_percentage"] = module_data["percentage"]
        self.data_dict[module_id + "_time"] = str(datetime.now().time())

    def parse_low_battery(self):
        # Decode the data as utf-8 and load into python dict
        module_data = self.msg.payload.decode("utf-8")
        module_data = json.loads(module_data)
        # Retrieve module data from python dict
        module_id = "M" + module_data["module-id"]

        self.data_dict[module_id + "_lowBattery"] = True
        self.data_dict[module_id + "_time"] = str(datetime.now().time())

    def make_temp_csv(self):
        # make sure that the temp file is
        current_dir = os.path.dirname(__file__)
        temp_filename = self.msg.topic.replace('/', '-')
        temp_file_path = os.path.join(current_dir,
                                      str('.~temp_' + temp_filename + '.csv'))

        fieldnames = []
        for key in self.data_dict.keys():
            fieldnames.append(key)

        if not os.path.exists(temp_file_path):
            # If the temp file does not exist write the headers for the CSV
            with open(temp_file_path, mode='a') as temp_file:
                csv_writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
                csv_writer.writeheader()

        with open(temp_file_path, mode='a') as temp_file:
            csv_writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
            csv_writer.writerow(self.data_dict)
