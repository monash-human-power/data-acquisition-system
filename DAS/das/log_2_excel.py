import logging
import os
import sqlite3
import json
import time

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from rich.logging import RichHandler

from mhp import topics
import paho.mqtt.client as mqtt


class DataLogger:

    def __init__(self, broker_ip='localhost', port=1883) -> None:
        self.v3_start = topics.V3.start
        self.broker_ip = broker_ip
        self.port = port
        self.mqtt_client = None

        #Data for log conversions
        # Load env variables
        load_dotenv()

        self.MQTT_LOG_FILE = os.getenv("MQTT_LOG_FILE")
        self.EXCEL_LOG_FILE = os.getenv("EXCEL_LOG_FILE")

        # Set logging to output all info by default
        logging.basicConfig(
            format="%(message)s",
            level=logging.INFO,
            handlers=[RichHandler()],
        )

    
    def on_connect(self, client, userdata, flags, rc):
        """Callback for when cleint receives a CONNNACK response."""
        print("Connected with result code " + str(rc))

        client.subscribe(str(self.v3_start))
    
    def on_disconnect(self, client, userdata, msg):
        """Callback called when user is disconnected from the broker."""
        print("Disconnected from broker")
    
    def on_log(self, client, userdata, level, buf):
        """The callback to log all MQTT information"""
        print("\nlog: ", buf)

    def on_message(self, client, userdata, msg):
        """The callback for when a PUBLISH message is received."""
        print(msg.topic + " " + str(msg.payload))

    def start(self):
        """Start Data Logger"""
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_log = self.on_log
        self.mqtt_client.on_disconnect = self.on_disconnect
        self.mqtt_client.connect_async(self.broker_ip, self.port, 60)

        self.mqtt_client.loop_start()
        while True:
            time.sleep(1)
    
    #Functions for log conversion
    def parse_module_data(self, module_id: int, cur: sqlite3.Cursor) -> pd.DataFrame:
        """Parses the module data if it is from the sensors"""

        query = f""" 
            SELECT * FROM LOG 
            WHERE TOPIC='{topics.WirelessModule.id(module_id).data}'
            """

        # Store all of the flattened data dicts inside a big array before converting to a dataframe
        data_arr = []
        for data_row in cur.execute(query).fetchall():
            # Unbundle SQL row into individual columns
            (id, run_id, unix_time, topic, message) = data_row

            # Decode binary string messages into json
            try:
                utf8_data = message.decode("utf-8")
                json_data = json.loads(utf8_data)
            except:
                logging.error(f"Message not utf-8 encoded. Skipping id:{id}.")
                continue

            # Retrieve sensor data from python dict
            data_dict = {"unix_time": unix_time, "run_id": run_id}
            for sensor in json_data["sensors"]:
                sensor_name = str(module_id) + "_" + sensor["type"]
                sensor_value = sensor["value"]

                # For nested sensor values
                if isinstance(sensor_value, dict):
                    for (sub_sensor, sub_sensor_value) in sensor_value.items():
                        sub_sensor_name = sensor_name + "_" + sub_sensor
                        data_dict[sub_sensor_name] = sub_sensor_value

                # For single sensor values
                else:
                    data_dict[sensor_name] = sensor_value

            data_arr.append(data_dict)

        return pd.DataFrame(data_arr)
    
    def parse_module_battery(self, module_id: int, cur: sqlite3.Cursor) -> pd.DataFrame:
        """Parses the module data if it is from the battery"""

        query = f""" 
            SELECT * FROM LOG 
            WHERE TOPIC='{topics.WirelessModule.id(module_id).battery}'
            """

        # Store all of the data dicts inside a big array before converting to a dataframe
        data_arr = []
        for data_row in cur.execute(query).fetchall():
            # Unbundle SQL row into individual columns
            (id, run_id, unix_time, topic, message) = data_row

            # Decode binary string messages into json
            try:
                utf8_data = message.decode("utf-8")
                json_data = json.loads(utf8_data)
            except:
                logging.error(f"Message not utf-8 encoded. Skipping id:{id}.")
                continue

            data_arr.append(
                {
                    "unix_time": unix_time,
                    "run_id": run_id,
                    f"{module_id}_voltage": json_data["voltage"],
                }
            )

        return pd.DataFrame(data_arr)

    def parse_all_raw(self, cur: sqlite3.Cursor) -> pd.DataFrame:
        """Convert all data in the LOG table into a single dataframe"""

        # Store all of the data dicts inside a big array before converting to a dataframe
        data_arr = []
        for data_row in cur.execute("SELECT * FROM LOG").fetchall():
            # Unbundle SQL row into individual columns
            (id, run_id, unix_time, topic, message) = data_row

            # Decode the data from a binary string to utf-8
            try:
                data_arr.append(
                    {
                        "id": id,
                        "topic": topic,
                        "unix_time": unix_time,
                        "run_id": run_id,
                        "data": message.decode("utf-8"),
                    }
                )
            except:
                logging.error(f"Message not utf-8 encoded. Skipping id:{id}.")
                continue

        return pd.DataFrame(data_arr)
    
    def convertXL(self):
        # Connect to the sqlite database that has all of the MQTT logs
        con = sqlite3.connect(self.MQTT_LOG_FILE)
        cur = con.cursor()

        with pd.ExcelWriter(self.EXCEL_LOG_FILE, engine="xlsxwriter") as writer:
            for module_id in [1, 2, 3, 4]:
                module_data = self.parse_module_data(module_id, cur)
                module_battery = self.parse_module_battery(module_id, cur)

                if not module_data.empty:
                    logging.info(f"Exporting wireless module {module_id} sensor data")
                    module_data.to_excel(
                        writer,
                        sheet_name=f"module_{module_id}_data",
                        index=False,
                    )

                if not module_battery.empty:
                    logging.info(f"Exporting wireless module {module_id} battery data")
                    module_battery.to_excel(
                        writer,
                        sheet_name=f"module_{module_id}_battery",
                        index=False,
                    )

            logging.info(f"Exporting all data to excel")
            self.parse_all_raw(cur).to_excel(writer, sheet_name="raw_data", index=False)

        con.close()


    


if __name__ == "__main__":
    
    data_logger = DataLogger()
    data_logger.start()
