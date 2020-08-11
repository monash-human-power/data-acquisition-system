import machine
import ubinascii
import utime
from mqtt_client import Client


try:
    import config
except FileNotFoundError:
    print('Error importing config.py, ensure a local version of config.py exists')


# Define module number and MQTT topics to publish to
MODULE_NUM = "2"
PUB_DATA_TOPIC = b"/v3/wireless-module/{}/data".format(MODULE_NUM)
PUB_TOPIC_LOW_BATTERY = b"/v3/wireless-module/{}/low-battery".format(MODULE_NUM)
PUB_BATTERY_TOPIC = b"/v3/wireless-module/{}/battery".format(MODULE_NUM)

# Topics to subscribe to
SUB_START = b"/v3/wireless-module/{}/start".format(MODULE_NUM)
SUB_STOP = b"/v3/wireless-module/{}/stop".format(MODULE_NUM)
SUB_TOPICS = [SUB_START, SUB_STOP]

# Generate a unique client_id to set up MQTT Client
client_id = ubinascii.hexlify(machine.unique_id())

# Variable to tell whether data should be sent or not
start_publish = False


# MQTT callback function
def sub_cb(topic, msg):
    """
    This function is called whenever we receive a message from one of the subscribed topics
    :param topic: The topic on which the message is received
    :param msg: The message received
    :changes made: The global variable 'start' is changed to True or False depending on which topic we receive the
                    message from
    """
    print("Successfully received message: ", msg, "on:", topic)
    global start_publish
    if topic == SUB_START:
        start_publish = True
    elif topic == SUB_STOP:
        start_publish = False


def restart_and_reconnect():
    print("Failed to connect to MQTT broker. Reconnecting...")
    utime.sleep(10)
    machine.reset()


def publish_test_messages(client, topic):
    """
    Keeps publishing data until a stop message is received
    :param client: An instance of the Client class
    :param topic: Topic to publish on
    """
    test_no = 0
    while start_publish:
        message = "Message sample " + str(test_no)
        client.mqtt_pub(topic, message)
        print("MQTT data sent: %s on %s through %s" % (message, PUB_DATA_TOPIC, config.MQTT_BROKER))

        client.check_for_message()

        utime.sleep(1)
        test_no = test_no + 1


def run_module():
    """
    Connects and publishes data using MQTT
    """
    # Create Client class instance
    my_client = Client(client_id, config.MQTT_BROKER)

    my_client.connect_and_subscribe(SUB_TOPICS, sub_cb)

    # Wait for the start message
    my_client.wait_for_message()

    # FIXME: Need to make this a continuous process (i.e keep checking for start message once a stop message is recieved)
    publish_test_messages(my_client, PUB_DATA_TOPIC)


run_module()
print("########## Reached end of file successfully #########")
