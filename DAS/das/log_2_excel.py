import logging
import os
import sqlite3
import json
import time
import argparse
import mqtt_logger
import numpy as np
import pandas as pd
import time
import paho.mqtt.client as mqtt

from dotenv import load_dotenv
from rich.logging import RichHandler
from datetime import datetime
from mhp import topics


class DataLogger:
    """Log run data into excel files.
    
    Parameters
    ----------
    db_file : str 
        Filepath to where the SQLite database will be stored.
    xl_file : str
        Filepath to where all Excel logs will be stored. 
    broker_ip : str 
        The hostname or IP of the MQTT broker, default value is 'localhost'
    port : int 
        The network port of the server host to connect to, default value is 1883.
    verbose: bool
        Sets the logginng output of Recorder, default value is False.
    username : str
        Username for MQTT broker.
    password : str
        Password for MQTT broker.
    fname : str
        Beginning portion of filenaming system, default value is 'runfile'.
    
    Attributes
    ----------
    v3_start : str
        The 'v3/start' topic.
    broker_ip : str 
        The hostname or IP of the MQTT broker, default value is 'localhost'
    port : int 
        The network port of the server host to connect to, default value is 1883.
    verbose: bool
        Sets the logginng output of Recorder, default value is False.
    username : str
        Username for MQTT broker.
    password : str
        Password for MQTT broker.
    mqtt_client: paho.mqtt.client
        MQTT client that connects to the broker and recives the messages.
    logging : bool
        Whether we are currently logging or not.
    MQTT_LOG_FILE : str 
        Filepath to where the SQLite database will be stored.
    EXCEL_LOG_FILE : str
        Filepath to where all Excel logs will be stored.
    time : str
        Time that a log begins recording, in HH-MM-SS format.
    recorder: mqtt_logger.Recorder
        Recorder class that will record MQTT logs into SQLite database.
    """

    def __init__(
        self, 
        db_file, 
        xl_file, 
        broker_ip='localhost', 
        port=1883, 
        verbose=False, 
        username=None, 
        password=None, 
        fname="runfile"
        ):

        self.v3_start = str(topics.V3.start)

        self.broker_ip = broker_ip
        self.port = port
        self.uname = username
        self.pword = password
        self.verbose = verbose
        self.mqtt_client = None

        self.logging = False
        self.MQTT_LOG_FILE = db_file 
        self.EXCEL_LOG_FILE = xl_file + fname
        self.time = "" 

        self.recorder = None


    def on_connect(self, client, userdata, flags, rc):
        """Callback for when client receives a CONNNACK response."""

        print("\nConnected with result code " + str(rc) + ".")
        client.subscribe(self.v3_start)
    

    def on_disconnect(self, client, userdata, msg):
        """Callback called when user is disconnected from the broker."""
        print("\nDisconnected from broker.")
    

    def on_log(self, client, userdata, level, buf):
        """The callback to log all MQTT information"""
        print("\nlog: ", buf)


    def on_message(self, client, userdata, msg):
        """The callback for when a PUBLISH message is received."""

        logging.info(f"\nReceived topic: " + str(msg.topic) + ", with message " + str(msg.payload))

        if msg.topic == self.v3_start:

            received_data = str(msg.payload.decode("utf-8"))
            dict_data = json.loads(received_data)

            if dict_data["start"]:

                if not self.logging:
                    self.start_logging()              
                else:
                    logging.warning("Already currently logging.")
            
            else:
                if self.logging:
                    self.stop_logging()
                else:
                    logging.warning("Logging not started yet.")


    def start_logging(self):
        """Start the Data Logger"""
        self.logging = True
        self.time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        self.recorder = mqtt_logger.Recorder(
            sqlite_database_path=self.MQTT_LOG_FILE+"MQTT_log_"+self.time+".db", 
            broker_address=self.broker_ip,
            verbose=self.verbose,
            username=self.uname,
            password=self.pword
            )

        self.recorder.start()


    def stop_logging(self):
        """Stop the Data Logger"""
        self.logging = False
        db_path = self.MQTT_LOG_FILE + "MQTT_log_" + self.time + ".db"
        xl_path = self.EXCEL_LOG_FILE + "_" + self.time + ".xlsx"
        self.convertXL(db_path, xl_path)

        self.recorder.stop()


    def start(self):
        """Start Data Logger & MQTT Client"""

        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        if self.uname is not None and self.pword is not None:
            self.mqtt_client.username_pw_set(self.uname, self.pword)
        self.mqtt_client.on_log = self.on_log
        self.mqtt_client.on_disconnect = self.on_disconnect
        self.mqtt_client.connect_async(self.broker_ip, self.port, 60)
        logging.info("Connected MQTT client.")

        self.mqtt_client.loop_start()
        while True:
            time.sleep(1)
    

    def stop(self):
        """Stops Data Logger & MQTT Client"""

        self.mqtt_client.disconnect()
        self.mqtt_client.loop_stop()
        logging.info("Disconnected MQTT client.")
    

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
        """Parses the module data if it is from the battery."""

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
        """Convert all data in the LOG table into a single dataframe."""

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
    

    def convertXL(self, db_path, xl_path):
        """Convert SQLite database logs into excel files."""

        # Connect to the sqlite database that has all of the MQTT logs
        con = sqlite3.connect(db_path)
        cur = con.cursor()

        with pd.ExcelWriter(xl_path, engine="xlsxwriter") as writer:
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


parser = argparse.ArgumentParser(
    description="Data Logger",
    add_help=True,
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)

parser.add_argument(
    "--host",
    action="store",
    type=str,
    default="localhost",
    help="""Address of the MQTT broker""",
)

parser.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    default=False,
    help="""Verbose logging output""",
)

parser.add_argument(
    "-u",
    "--username",
    action="store",
    type=str,
    default=None,
    help="""Username for MQTT broker""",
)

parser.add_argument(
    "-p",
    "--password",
    action="store",
    type=str,
    default=None,
    help="""Password for MQTT broker""",
)

parser.add_argument(
    "-f",
    "--filename",
    action="store",
    type=str,
    default="runfile",
    help="""File naming system for excel conversion.""",
)

if __name__ == "__main__":

    # Load env variables
    load_dotenv()
    mqtt_log_file = os.getenv("MQTT_LOG_FILE")
    excel_log_file = os.getenv("EXCEL_LOG_FILE")

    # Read command line arguments
    args = parser.parse_args()

    logging.basicConfig(
        format="%(levelname)-8s [%(filename)s] %(message)s", level=logging.INFO
    )

    DATA_LOGGER = DataLogger(
        db_file=mqtt_log_file,
        xl_file=excel_log_file,
        broker_ip=args.host,
        verbose=args.verbose,
        username=args.username,
        password=args.password,
        fname=args.filename
    )

    DATA_LOGGER.start()
