# Author: Kunj
# Last Modified: 3/08/2020
import paho.mqtt.client as mqtt
import time

client = mqtt.Client("my_id")

MODULE_NUM = "2"
START_TOPIC = '/v3/wireless-module/{}/start'.format(MODULE_NUM)
STOP_TOPIC = '/v3/wireless-module/{}/stop'.format(MODULE_NUM)
SUB_DATA_TOPIC = '/v3/wireless-module/{}/data'.format(MODULE_NUM)

# Broker domain name or IP address
BROKER = "5.196.95.208"


def on_connect(client, data, message):
    print("Received: ", str(message.payload.decode("utf-8")))
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
    print("Sending first start message")
    for i in range(4):
        client.publish(START_TOPIC, b'You can start now')
        time.sleep(1)
    print("Sent all start messages")

    # Wait for data to receive
    time.sleep(10)

    client.publish(STOP_TOPIC, b'You can stop now')
    client.publish(STOP_TOPIC, b'You can stop now')
    print("Sent stop message")
client.loop_stop()



