import time
import machine
import ubinascii
import fake

try:
    import config
except ImportError:
    print("Config file not supplied. Add config.py")

# Use micro pip to install packages
import upip
upip.install("micropython-umqtt.simple2")
from umqtt.simple import MQTTClient


# Define module number and MQTT topics
MODULE_NUM = "1"
FAKE_MODULE = fake.module(MODULE_NUM)

PUB_DATA = b'/v3/wireless-module/{}/data'.format(MODULE_NUM)
PUB_BATTERY = b'/v3/wireless-module/{}/battery'.format(MODULE_NUM)
PUB_LOW_BATTERY = b'/v3/wireless-module/{}/low-battery'.format(MODULE_NUM)

SUB_LED = b'/v3/wireless-module/{}/LED'.format(MODULE_NUM)
SUB_TOPICS = [SUB_LED]


# Set up MQTT client by generating a client_id
client_id = ubinascii.hexlify(machine.unique_id())

# MQTT callbacks
def sub_cb(topic, msg):
    print((topic, msg))

    if topic == SUB_LED and msg == b'on':
        print('ESP received: LED ON')
        builtin_LED.on()

    if topic == SUB_LED and msg == b'off':
        print('ESP received: LED OFF')
        builtin_LED.off()

def connect_and_subscribe(client_id, mqtt_server, sub_topics):
    client = MQTTClient(client_id, mqtt_server)
    client.set_callback(sub_cb)
    client.connect()
    print('Connected to %s MQTT broker' % (mqtt_server))
    for topic in sub_topics:
        client.subscribe(topic)
        print('Subscribed to %s topic' % (topic))
    return client

def restart_and_reconnect():
    print('Failed to connect to MQTT broker. Reconnecting...')
    time.sleep(10)
    machine.reset()

# Converts into a form MQTT can read
def to_bytes_literal(data):
    str_data = str(data)
    return str.encode(str_data)

# This functions takes care of all of the formating and just publishes to a topic
def MQTT_pub(data, topic):
    try:
        client.check_msg()
        msg = to_bytes_literal(data)
        client.publish(topic, msg)
        print("MQTT data sent: %s on %s" % (msg, topic))

    except OSError:
        restart_and_reconnect()


# Try to connect to MQTT server, restart device if it times out
try:
    client = connect_and_subscribe(client_id, config.MQTT_BROKER, SUB_TOPICS)
except OSError:
    config.red_LED.on()
    restart_and_reconnect()

# Set up data recording timers / interupts
def send_data(timer):
    MQTT_pub(FAKE_MODULE.data(), PUB_DATA)

def send_battery(timer):
    MQTT_pub(FAKE_MODULE.battery(), PUB_DATA)

def send_low_battery(timer):
    placeholder_battery_charge = 50
    if placeholder_battery_charge < 10:
        MQTT_pub(FAKE_MODULE.battery(), PUB_BATTERY)

# Update status lights
config.orange_LED.off()
config.red_LED.off()
config.green_LED.on()

# Sends data every second
data_timer = machine.Timer(0) 
data_timer.init(period=1000, mode=machine.Timer.PERIODIC, callback=send_data)

# Sends battery info every 5 minutes
battery_timer = machine.Timer(1) 
battery_timer.init(period=300000, mode=machine.Timer.PERIODIC, callback=send_battery)

# If low battery send data every 5 seconds
low_battery_timer = machine.Timer(2) 
low_battery_timer.init(period=10000, mode=machine.Timer.PERIODIC, callback=send_low_battery)