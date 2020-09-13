import machine
from mpu import Mpu
from wireless_module import WirelessModule
from co2_sensor import CO2
from dht_sensor import DhtSensor

# Define module number
MODULE_NUM = "2"

# RZERO (for calibration of MQ135) found when the sensor was first 'activated'
RZERO = 8.62

# Define all the Pin objects for each sensor
scl_pin = machine.Pin(22)
sda_pin = machine.Pin(21)
dht_pin = machine.Pin(4)
mq135_pin = machine.Pin(34)

# Instantiate sensor objects
my_mpu = Mpu(scl_pin, sda_pin, 100)
my_mpu.calibrate()
my_dht = DhtSensor(dht_pin)
my_mq135 = CO2(mq135_pin)
my_mq135.set_rzero(RZERO)

# Set up the wireless module
middle_module = WirelessModule(MODULE_NUM)
sensors = [my_mpu, my_dht, my_mq135]
middle_module.add_sensors(sensors)

# Enters an infinite loop
print("starting loop")
middle_module.run()
