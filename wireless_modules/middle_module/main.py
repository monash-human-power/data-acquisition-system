# Note: You can remove all the PRINT statements when everything is already tested

import machine
# from wireless_module import WirelessModule
# from sensors.dht import DHTSensor
import ubinascii
import utime

# To get access to the 'MQTT_BROKER' variable in config.py
try:
    import config
except FileNotFoundError:
    print('Error importing config.py, ensure a local version of config.py exists')

# To get access to the Client class in the MQTT_Client_class file
try:
    from MQTT_Client_class import Client
except:
    print("Error importing MQTT_Client_class.py, ensure a local version of the file exists")

# Define module number and MQTT topics to publish to
MODULE_NUM = '2'
PUB_DATA_TOPIC = b'/v3/wireless-module/{}/data'.format(MODULE_NUM)
PUB_TOPIC_LOW_BATTERY = b'/v3/wireless-module/{}/low-battery'.format(MODULE_NUM)
PUB_BATTERY_TOPIC = b'/v3/wireless-module/{}/battery'.format(MODULE_NUM)

# Topics to subscribe to
SUB_START = b'/v3/wireless-module/{}/start'.format(MODULE_NUM)
SUB_STOP = b'/v3/wireless-module/{}/stop'.format(MODULE_NUM)
SUB_TOPICS = [SUB_START, SUB_STOP]

# Generate a unique client_id to set up MQTT Client
client_id = ubinascii.hexlify(machine.unique_id())

# Variable to tell whether data should be sent or not
start_publish = False


# MQTT callback function
def sub_cb(topic, msg):
    """
    This function is called whenever a subscribed topic sends a message and we read it through either calling
    client.check_msg() or client.wait_msg()
    :param topic: The topic on which the message is received
    :param msg: The message received
    :return: None
    :changes made: The global variable 'start' is changed to True or False depedning on which topic we receive the
                    message from
    """
    print('Successfully received message: ', msg, 'on:', topic)
    if topic == SUB_START:
        global start_publish
        start_publish = True
    elif topic == SUB_STOP:
        global start_publish
        start_publish = False


def restart_and_reconnect():
    print('Failed to connect to MQTT broker. Reconnecting...')
    utime.sleep(10)
    machine.reset()


# Create Client class instance
my_client = Client(client_id, config.MQTT_BROKER)

if not my_client.connect_and_subscribe(SUB_TOPICS, sub_cb):
    # If the connect_and_subscribe returns False, a connection to the broker could not be established
    restart_and_reconnect()

# Wait for the start message
my_client.wait_for_message()

# Keep publishing data till a stop message is received
test_no = 0
while start_publish:
    print('----------publishing-----------')
    message = 'Message sample ' + str(test_no)
    my_client.mqtt_pub(message, PUB_DATA_TOPIC)
    print('MQTT data sent: %s on %s through %s' % (message, PUB_DATA_TOPIC, config.MQTT_BROKER))

    # Keep checking for an incoming messages (specifically the stop message)
    my_client.check_for_message()

    utime.sleep(1)
    test_no = test_no + 1

print('########## Reached end of file successfully #########')


