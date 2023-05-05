import sys
sys.path.insert(1, '../sensors')
from sensors.pressure_sensor import PressureSensor
sys.path.insert(2, '../')
from wireless_module import WirelessModule
import config
import logging
import asyncio


MODULE_NUM = 5


async def main():
    logging.basicConfig(
        format="%(levelname)-8s [%(filename)s] %(message)s", level=logging.DEBUG
    )

    pressure_sensor_address = 76
    my_pressure_sensor = PressureSensor(pressure_sensor_address)

    pressure_module = WirelessModule(MODULE_NUM)
    sensors = [my_pressure_sensor]
    pressure_module.add_sensors(sensors)

    logging.debug("Start asyncio loop")
    asyncio.create_task(pressure_module.run())

    while True:
        await asyncio.sleep(1)


asyncio.run(main())
