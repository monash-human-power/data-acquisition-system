import paho.mqtt.client as mqtt
import time
import argparse

parser = argparse.ArgumentParser(
    description='MQTT wireless module test script with dummy payloads',
    add_help=True)
parser.add_argument(
    '--module', action='store', type=int,
    default=2, help="""The module number to determine the publish and subscription topics. 
    If nothing is selected it will send on module number 2 topics.""")
parser.add_argument(
    '--host', action='store', type=str, default="localhost",
    help="""Address of the MQTT broker.""")


def on_msg_receive(client, data, message):
    print('Received: ', str(message.payload.decode('utf-8')))
    return True


if __name__ == "__main__":
    client = mqtt.Client()
    args = parser.parse_args()

    MODULE_NUM = args.module

    START_TOPIC = f'/v3/wireless-module/{MODULE_NUM}/start'
    STOP_TOPIC = f'/v3/wireless-module/{MODULE_NUM}/stop'
    SUB_DATA_TOPIC = f'/v3/wireless-module/{MODULE_NUM}/data'

    # Broker domain name or IP address
    BROKER = args.host
    client.connect(BROKER)

    # Set function to call when a message from the subscribed topic is received
    client.on_message = on_msg_receive
    client.subscribe(SUB_DATA_TOPIC)

    # The start loop starts scanning for incoming messages and the stop loop stops this process.
    client.loop_start()

    # Give some time for ESP32 to "set-up"
    time.sleep(2)

    print('Sending start message')
    # QOS=1 ensures the message is received at least once
    client.publish(START_TOPIC, qos=1)

    # Wait for data to receive
    time.sleep(5)

    client.publish(STOP_TOPIC, qos=1)
    print('Sent stop message')
    client.loop_stop()
