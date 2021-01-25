import sys
import time
import uasyncio as asyncio
import machine
from wireless_module import WirelessModule
from co2_sensor import CO2
from gps_sensor import GpsSensor
from reed_sensor import ReedSensor


# Define module number
MODULE_NUM = "3"

# RZERO (for calibration of MQ135) found when the sensor was first 'activated'
RZERO = 8.62

# Circumference of a 700x28 bike wheel in meters.
WHEEL_CIRCUMFERENCE = 2.136


async def main():
    # Define all the Pin objects for each sensor
    mq135_pin = machine.Pin(34)
    reed_pin = machine.Pin(5)

    # Instantiate sensor objects
    my_mq135 = CO2(mq135_pin)
    my_mq135.set_rzero(RZERO)

    my_gps = GpsSensor(2)

    my_reed = ReedSensor(reed_pin, WHEEL_CIRCUMFERENCE)

    # Set up the wireless module
    back_module = WirelessModule(MODULE_NUM)
    sensors = [my_mq135, my_gps, my_reed]
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
