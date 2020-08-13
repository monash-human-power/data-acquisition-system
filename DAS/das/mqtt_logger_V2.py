# TODO: Add playback
# TODO: Add nicer saving and filtering
# TODO: Do propper error checking
# TODO: Check that it exits nicely

import paho.mqtt.client as mqtt
from datetime import datetime
from pathlib import Path
import argparse
import os

# Set current file path and csv_data directory
CURRENT_FILEPATH = os.path.dirname(__file__)
CSV_FILEPATH = os.path.join(CURRENT_FILEPATH, "csv_data")

# Create csv_data folder if none exists
Path(CSV_FILEPATH).mkdir(parents=True, exist_ok=True)

# Name the csv log file (APPEND ONLY)
FILENAME = "log.csv"
LOG_FILEPATH = os.path.join(CSV_FILEPATH, FILENAME)
LOG_FILE = open(LOG_FILEPATH, "a")

# Record current datetime to produce time deltas
DATETIME_START = datetime.now()

parser = argparse.ArgumentParser(
    description='MQTT wireless logger',
    add_help=True)

parser.add_argument(
    '--host', action='store', type=str, default="localhost",
    help="""Address of the MQTT broker. If nothing is selected it will
    default to localhost.""")


def on_connect(client, userdata, flags, rc):
    # TODO: add actual error handling
    if rc == 0:
        print("Connected Successfully! Result code: " + str(rc))
    else:
        print("Something went wrong! Result code: " + str(rc))

    # Subscribe to all of the topics
    try: 
        client.subscribe("#")
    except Exception as e:
        print(e)


def on_message(client, userdata, msg):
    # Log the incoming MQTT message
    try:
        log(msg.topic, msg.payload)
    except Exception as e:
        print(e)


def log(mqtt_topic, message) -> None:
    time_delta = datetime.now() - DATETIME_START
    print(f"{time_delta} | {mqtt_topic} | {message}")

    # Write data to csv file
    LOG_FILE.write(f"{time_delta}, {mqtt_topic}, {message} \n")


if __name__ == "__main__":
    args = parser.parse_args()
    broker_address = args.host
    client = mqtt.Client()

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(broker_address)

    client.loop_forever()
