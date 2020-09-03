import machine
import ubinascii
from mpu import Mpu
from wireless_module import WirelessModule
from mq135_sensor import co2
from dht_sensor import DhtSensor

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

# Generate a unique client_id used to set up MQTT Client
CLIENT_ID = ubinascii.hexlify(machine.unique_id())

# Define all the Pin objects for each sensor
scl_pin = machine.Pin(22)
sda_pin = machine.Pin(21)
dht_pin = machine.Pin(4)
mq135_pin = machine.Pin(34)

# Change ADC resolution
adc = machine.ADC(mq135_pin)
adc.width(machine.ADC.WIDTH_10BIT)

# Instantiate sensor objects
my_mpu = Mpu(scl_pin, sda_pin)
my_dht = DhtSensor(dht_pin, 2)
my_mpu.calibrate()
my_mq135 = co2(mq135_pin)
my_mq135.set_rzero(8.62)

# Set up the wireless module
middle_module = WirelessModule(CLIENT_ID, config.MQTT_BROKER)
middle_module.set_sub_topics(SUB_START, SUB_STOP)
middle_module.set_pub_topics(PUB_DATA_TOPIC, PUB_BATTERY_TOPIC, PUB_TOPIC_LOW_BATTERY)
sensors = [my_mpu, my_dht, my_mq135]
middle_module.add_sensors(sensors)

# Enters an infinite loop
print("starting loop")
middle_module.run()
