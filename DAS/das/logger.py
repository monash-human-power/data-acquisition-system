from pathlib import Path
from datetime import datetime
import paho.mqtt.client as mqtt
import os


class Logger:
    """ This class logs MQTT data"""

    def __init__(self, csv_folder_path: str, broker_address: str = "localhost", verbose: bool = True, *topics: str) -> None:
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

        # Name the csv log file (APPEND ONLY)
        # TODO: Make variable
        filename = "0001_log.csv"
        self._LOG_FILE = open(os.path.join(csv_folder_path, filename), "a")

        # Connect to MQTT broker
        self._client = mqtt.Client()

        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message

        self._client.connect(broker_address)
        # self._client.loop_start()  # Threaded
        self._client.loop_forever()

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected Successfully! Result code: " + str(rc))
        else:
            print("Something went wrong! Result code: " + str(rc))

        # Subscribe to all of the topics
        try:
            for topic in self.TOPICS:
                self._client.subscribe(topic)
        except Exception as e:
            print(e)

    def _on_message(self, client, userdata, msg):
        # Log the incoming MQTT message
        try:
            self.log(msg.topic, msg.payload)
        except Exception as e:
            print(e)

    def log(self, mqtt_topic: str, message: str) -> None:
        time_delta = datetime.now() - self._DATETIME_START

        if self._VERBOSE:
            print(f"{time_delta} | {mqtt_topic} | {message}")

        # Write data to csv file
        self._LOG_FILE.write(f"{time_delta}, {mqtt_topic}, {message} \n")
