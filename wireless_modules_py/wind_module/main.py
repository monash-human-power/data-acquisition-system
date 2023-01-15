import config
import logging
import asyncio
from wireless_module import WirelessModule
from wind_sensor import WindSensor
import sys
sys.path.insert(1, '../sensors')
sys.path.insert(2, '../')


# define module number
MODULE_NUM = 5


async def main():
    logging.basicConfig(
        format="%(levelname)-8s [%(filename)s] %(message)s", level=logging.DEBUG
    )

    # define the port that the wind sensor is connected to
    wind_sensor_port = config.PORT

    # instantiate a wind sensor
    my_wind_sensor = WindSensor(wind_sensor_port)

    # set up the wind module
    wind_module = WirelessModule(MODULE_NUM)
    sensors = [my_wind_sensor]
    wind_module.add_sensors(sensors)

    logging.debug("Start asyncio loop")
    asyncio.create_task(wind_module.run())

    # keep code running indefinitely
    while True:
        await asyncio.sleep(1)


asyncio.run(main())
