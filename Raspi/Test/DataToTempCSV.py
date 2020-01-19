import json
from datetime import datetime
import os
import csv

class DataToTempCSV:
    def __init__(self, msg):
        self.msg = msg
        self.data_dict = {}

        # if msg.topic[:18] == "v3/wireless-sensor" and msg.topic[-4:] == "data":
        self.parse_wireless_module_data()
        self.make_temp_csv()


    def parse_wireless_module_data(self):
        module_data = self.msg.payload.decode("utf-8")    # Decode the data as utf-8
        module_data = json.loads(module_data)           # Load from json to dict
        sensor_data = module_data["sensors"]        # Retrieve sensor data
        module_id = str("M" + self.msg.topic[19])        # Find module ID

        for sensor in sensor_data:
            sensor_type = module_id + "_" + sensor["type"]
            sensor_value = sensor["value"]

            if isinstance(sensor_value, dict):
                pass
            else:
                self.data_dict[sensor_type] = sensor_value

        # Add in the time and date that the data came in
        self.data_dict[module_id + "_time"] = str(datetime.now().time())


    def make_temp_csv(self):
        # make sure that the temp file is
        current_dir = os.path.dirname(__file__)
        temp_filename = self.msg.topic.replace('/', '-')
        temp_file_path = os.path.join(current_dir, str('.~temp_' + temp_filename + '.csv'))

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
