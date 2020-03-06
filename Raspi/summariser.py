import argparse
import json
from time import sleep
import paho.mqtt.client as mqtt

parser = argparse.ArgumentParser(description='DAS MQTT python script', add_help=True)
parser.add_argument('--host', action='store', type=str, default="localhost", help="address of the MQTT broker")
parser.add_argument('--port', action='store', type=int, default=1883, help="address of the MQTT broker")
parser.add_argument('--username', action='store', type=str, help="username for the MQTT broker (optional)")
parser.add_argument('--password', action='store', type=str, help="password for the MQTT broker (optional)")

data_cache = {}

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("/v3/wireless-module/+/data")

def on_message(client, userdata, msg):
    json_msg = json.loads(msg.payload.decode("utf-8"))
    sensors = json_msg["sensors"]
    for sensor in sensors:
        if sensor["type"] == "gps":
            data_cache["gpsla"] = sensor["value"]["latitude"]
            data_cache["gpslo"] = sensor["value"]["longitude"]
            data_cache["gpss"] = sensor["value"]["speed"]
        elif sensor["type"] == "power":
            data_cache["p"] = sensor["value"]

def start_loop(client):
    while True:
        payload = json.dumps(data_cache, separators=(",", ":"))
        client.publish("/v3/data-summary", payload)
        sleep(5)


if __name__ == "__main__":
    args = parser.parse_args()

    broker_address = args.host
    broker_port = args.port
    client = mqtt.Client()

    client.on_connect = on_connect
    client.on_message = on_message

    broker_username = args.username
    broker_password = args.password
    if broker_username is not None:
        client.username_pw_set(broker_username, broker_password)

    client.connect(broker_address, port=broker_port)
    client.loop_start()
    start_loop(client)
