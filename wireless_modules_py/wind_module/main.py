import sys
sys.path.insert(1, '../sensors')
from wind_sensor import WindSensor
sys.path.insert(2, '../')
from wireless_module import WirelessModule
import asyncio
import logging


# define module number
MODULE_NUM = 4


async def main():
    logging.basicConfig(
        format="%(levelname)-8s [%(filename)s] %(message)s", level=logging.DEBUG
    )
    
    anemometer_port = "COM3"
    my_anemometer = WindSensor(anemometer_port)
    
    wind_module = WirelessModule(MODULE_NUM)
    sensors = [my_anemometer]
    wind_module.add_sensors(sensors)
    
    logging.debug("Start asyncio loop")
    asyncio.create_task(wind_module.run())
    
    # keep code running indefinitely
    while True:
        await asyncio.sleep(1)


asyncio.run(main())