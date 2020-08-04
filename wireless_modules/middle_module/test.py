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
    '--host', action='store', type=str, default="5.196.95.208",
    help="""Address of the MQTT broker. If nothing is selected it will
    default to 5.196.95.208 - a test server by mosquito.""")


if __name__ == "__main__":
    client = mqtt.Client('my_id')
    args = parser.parse_args()

    MODULE_NUM = args.module

    # MODULE_NUM = '2'
    START_TOPIC = f'/v3/wireless-module/{MODULE_NUM}/start'
    STOP_TOPIC = f'/v3/wireless-module/{MODULE_NUM}/stop'
    SUB_DATA_TOPIC = f'/v3/wireless-module/{MODULE_NUM}/data'

    # Broker domain name or IP address
    BROKER = args.host

    def on_connect(client, data, message):
        print('Received: ', str(message.payload.decode('utf-8')))
        return True

    # Connect to the Broker
    client.connect(BROKER)

    # Calls the function on_connect whenever a message is received
    client.on_message = on_connect
    client.subscribe(SUB_DATA_TOPIC)

    # The start loop starts scanning for incoming messages and the stop loop stops this process.
    client.loop_start()
    for i in range(1):
        client.subscribe(SUB_DATA_TOPIC)
        # Wait more than 10 seconds in case, main.py could not connect to the broker and takes 10 seconds to restart
        time.sleep(11)
        # Send repeatedly to make sure it's received
        print('Sending first start message')
        for j in range(4):
            client.publish(START_TOPIC, b'You can start now')
            time.sleep(1)
        print('Sent all start messages')

        # Wait for data to receive
        time.sleep(10)

        client.publish(STOP_TOPIC, b'You can stop now')
        client.publish(STOP_TOPIC, b'You can stop now')
        print('Sent stop message')
    client.loop_stop()



