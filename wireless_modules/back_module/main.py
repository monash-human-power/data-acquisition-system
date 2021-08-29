import sys
import time
import uasyncio as asyncio
import machine
from wireless_module import WirelessModule
from co2_sensor import CO2
from dht_sensor import DhtSensor
from gps_sensor import GpsSensor
from mpu_sensor import MpuSensor
from reed_sensor import ReedSensor
from battery_reader import BatteryReader


# Define module number
MODULE_NUM = "3"

# RZERO (for calibration of MQ135) found when the sensor was first 'activated'
# This can be found by allowing the CO2 reading to stabilise in an atmosphere
# known to be closish to 400ppm (i.e. outside) and reading the printed rzero
# on serial.
RZERO = 6.1

# Circumference of a 700x28 bike wheel in meters.
WHEEL_CIRCUMFERENCE = 2.136

# Define a function to map measured voltages to "true" voltages.
# See util/battery_lin_reg.py
def battery_calibration(voltage):
    return 0.710 * voltage + 0.927


# Pins for R, G, B channels of status LED
STATUS_PINS = [14, 12, 13]


async def main():
    for pin_num in STATUS_PINS:
        pin = machine.Pin(pin_num, machine.Pin.OUT)
        pin.off()

    # Define all the Pin objects for each sensor
    dht_pin = machine.Pin(4)
    reed_pin = machine.Pin(5)
    sda_pin = machine.Pin(21)
    scl_pin = machine.Pin(22)
    mq135_pin = machine.Pin(34)

    # Instantiate sensor objects
    my_dht = DhtSensor(dht_pin)

    my_mq135 = CO2(mq135_pin)
    my_mq135.set_rzero(RZERO)

    my_reed = ReedSensor(reed_pin, WHEEL_CIRCUMFERENCE)

    my_gps = GpsSensor(2)

    my_mpu = MpuSensor(scl_pin, sda_pin, 20)
    my_mpu.calibrate()

    battery_pin = 32
    battery_reader = BatteryReader(battery_pin, battery_calibration)

    # Set up the wireless module
    back_module = WirelessModule(MODULE_NUM, battery_reader)
    sensors = [my_dht, my_mq135, my_reed, my_gps, my_mpu]
    back_module.add_sensors(sensors)

    print("Starting asyncio loop")
    asyncio.create_task(back_module.run())

    # Keep our code running indefinitely - the above call won't block!
    while True:
        await asyncio.sleep(1)


try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("KeyboardInterrupt, exiting...")
except Exception as exc:
    sys.print_exception(exc)
    print("Detected crash, resetting in 5 seconds...")
    time.sleep(5)
    machine.reset()
