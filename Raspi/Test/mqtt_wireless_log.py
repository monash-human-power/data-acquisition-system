import csv
import json
import argparse
import paho.mqtt.client as mqtt

"""
1. Subscribe to the chanels
2. Capture and decode the JSON
3. Convert the json to csv
4. append the data to the csv file

# NOTE: The battery will be implemented later. Just do the key data first.

"""


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected Sucessfully! Result code: " + str(rc))
    else:
        print("Something went wrong! Result code: " + str(rc))


def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload.decode("utf-8")))


if __name__ == "__main__":
    broker_address = 'localhost'
    client = mqtt.Client()

    client.on_connect = on_connect
    client.on_message = on_message

    # Subscribe to all of the data topics
    client.subscribe("/v3/wireless-module/1/data")
    client.subscribe("/v3/wireless-module/2/data")
    client.subscribe("/v3/wireless-module/3/data")

    # Subscribe to all of the battery topics
    client.subscribe("/v3/wireless-module/battery/low")
    client.subscribe("/v3/wireless-module/1/battery")
    client.subscribe("/v3/wireless-module/2/battery")
    client.subscribe("/v3/wireless-module/3/battery")

    client.connect(broker_address)
    client.loop_start()
    client.loop_stop()
