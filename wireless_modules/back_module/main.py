import sys
import time
import uasyncio as asyncio
import machine
from wireless_module import WirelessModule
from co2_sensor import CO2
from dht_sensor import DhtSensor
from gps_sensor import GpsSensor
from reed_sensor import ReedSensor
from battery_reader import BatteryReader


# Define module number
MODULE_NUM = "3"

# RZERO (for calibration of MQ135) found when the sensor was first 'activated'
RZERO = 6.1

# Circumference of a 700x28 bike wheel in meters.
WHEEL_CIRCUMFERENCE = 2.136

# Define Voltage divider factor for this module or leave as None to use default voltage factor
VOLTAGE_FACTOR = None
SCALE_FACTOR = 4.13 / 4.64


async def main():
    # Define all the Pin objects for each sensor
    dht_pin = machine.Pin(4)
    mq135_pin = machine.Pin(34)
    reed_pin = machine.Pin(5)

    # Instantiate sensor objects
    my_dht = DhtSensor(dht_pin)

    my_mq135 = CO2(mq135_pin)
    my_mq135.set_rzero(RZERO)

    my_reed = ReedSensor(reed_pin, WHEEL_CIRCUMFERENCE)

    my_gps = GpsSensor(2)

    battery_pin = 32
    battery_reader = BatteryReader(
        battery_pin, scale=SCALE_FACTOR, voltage_factor=VOLTAGE_FACTOR
    )

    # Set up the wireless module
    back_module = WirelessModule(MODULE_NUM, battery_reader)
    sensors = [my_dht, my_mq135, my_reed, my_gps]
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
