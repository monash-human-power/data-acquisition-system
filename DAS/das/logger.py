from pathlib import Path
from datetime import datetime
import paho.mqtt.client as mqtt
import os


class Logger:
    """ This class logs MQTT data """

    def __init__(self, csv_folder_path: str, *topics: str, broker_address: str = "localhost", verbose: bool = True) -> None:
        # The logger object can subscribe to many topics (if none are selected then it will subscrive to all)
        if len(topics) != 0:
            self.TOPICS = topics
        else:
            self.TOPICS = ("#")

        # Whether or not it prints out as it records
        self._VERBOSE = verbose

        # Record current datetime to produce time deltas
        self._DATETIME_START = datetime.now()

        # Create csv_data folder if none exists
        Path(csv_folder_path).mkdir(parents=True, exist_ok=True)

        # Name the csv log file xxxx_log.csv where xxxx is a number
        # APPEND ONLY to stop accidentally recording over data
        previous_log_num = 0
        for filename in os.listdir(csv_folder_path):
            try:
                if int(filename[0:4]) > previous_log_num:
                    previous_log_num = int(filename[0:4])
            except ValueError:
                print(
                    f"WARNING: {filename} should not be in {csv_folder_path}")
            except Exception as e:
                print(f"ERROR: {e}")

        # fstring :0>4 used to ensure that the number will always be 4 long
        filename = f"{previous_log_num + 1:0>4}_log.csv"
        self._LOG_FILE = open(os.path.join(csv_folder_path, filename), "a")
        # Add headers for csv
        self._LOG_FILE.write("time_delta, mqtt_topic, message \n")

        # Connect to MQTT broker
        self._client = mqtt.Client()

        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message

        self._client.connect(broker_address)
        # self._client.loop_start()  # Threaded
        self._client.loop_forever()

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connection Successful!")
        else:
            print("ERROR: Something went wrong!")

        # Subscribe to all of the topics
        try:
            for topic in self.TOPICS:
                self._client.subscribe(topic)
                if self._VERBOSE:
                    print(f"Subscribed to: {topic}")
        except Exception as e:
            print(f"ERROR: {e}")

    def _on_message(self, client, userdata, msg):
        # Log the incoming MQTT message
        try:
            self.log(msg.topic, msg.payload)
        except Exception as e:
            print(f"ERROR: {e}")

    def log(self, mqtt_topic: str, message: str) -> None:
        time_delta = datetime.now() - self._DATETIME_START

        # Write data to csv file
        try:
            self._LOG_FILE.write(f"{time_delta}, {mqtt_topic}, {message} \n")
            if self._VERBOSE:
                # TODO: don't hardcode topic length when printing
                print(f"{time_delta} | {mqtt_topic: <50} | {message}")
        except Exception as e:
            print(f"ERROR: {e}")
