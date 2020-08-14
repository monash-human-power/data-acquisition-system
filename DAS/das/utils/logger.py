from pathlib import Path
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import csv
import time
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

        # Record current time to produce time deltas
        self._TIME_START = time.monotonic()

        # Create csv_data folder if none exists
        Path(csv_folder_path).mkdir(parents=True, exist_ok=True)

        # Name the csv log file xxxx_log.csv where xxxx is a number
        # APPEND ONLY to stop accidentally recording over data
        previous_log_num = 0
        for filename in os.listdir(csv_folder_path):
            try:
                if int(filename[0:4]) > previous_log_num:
                    previous_log_num = abs(int(filename[0:4]))
            except ValueError:
                print(
                    f"WARNING: {filename} should not be in {csv_folder_path}")
            except Exception as e:
                print(f"ERROR: {e}")

        # fstring :0>4 used to ensure that the number will always be 4 long
        filename = f"{previous_log_num + 1:0>4}_log.csv"
        self._LOG_FILE = open(os.path.join(csv_folder_path, filename), "a")
        self._LOG_FILE_WRITER = csv.DictWriter(
            self._LOG_FILE,
            delimiter=',',
            quotechar='`',
            quoting=csv.QUOTE_ALL,
            fieldnames=["time_delta", "mqtt_topic", "message"])

        # Add headers for csv
        self._LOG_FILE_WRITER.writeheader()

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
            self.log(msg.topic, msg.payload.decode('utf-8'))
        except Exception as e:
            print(f"ERROR: {e}")

    def log(self, mqtt_topic: str, message: str) -> None:
        time_delta = time.monotonic() - self._TIME_START

        # Write data to csv file
        try:
            self._LOG_FILE_WRITER.writerow(
                {'time_delta': time_delta,
                 'mqtt_topic': mqtt_topic,
                 'message': message})
            if self._VERBOSE:
                # TODO: Don't hardcode topic length when printing (<50)
                print(
                    f"{round(time_delta, 5): <10} | {mqtt_topic: <50} | {message}")
        except Exception as e:
            print(f"ERROR: {e}")


class Playback:
    def __init__(self, filepath: str, broker_address: str = "localhost", verbose: bool = True) -> None:
        self._VERBOSE = verbose
        self._BROKER = broker_address

        # Read in make an array of functions
        log_file = open(filepath, "r")
        csv_reader = csv.DictReader(
            log_file,
            delimiter=',',
            quotechar='`',
            quoting=csv.QUOTE_ALL,
            skipinitialspace=True)

        # Place each row in
        self._log_data = []
        simple_q = [0, 0]
        for row in csv_reader:
            row["time_delta"] = float(row["time_delta"])

            # Move the queue along one
            simple_q = [row["time_delta"], simple_q[0]]

            # The amount of sleep time is the difference between the two time_deltas
            row["sleep_time"] = abs(simple_q[0] - simple_q[1])
            self._log_data.append(row)

    def play(self, speed: float = 1) -> None:
        if self._VERBOSE:
            print(f"⚡ Playback initiated at {speed}x speed ⚡")

        for row in self._log_data:
            scaled_sleep = row["sleep_time"] * (1/speed)
            time.sleep(scaled_sleep)
            publish.single(row["mqtt_topic"], row["message"],
                           hostname=self._BROKER)
            if self._VERBOSE:
                print(
                    f"{round(row['time_delta'], 5): <10} | {round(scaled_sleep, 5): <10} | {row['mqtt_topic']: <50} | {row['message']}")
