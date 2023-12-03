import sys
sys.path.insert(1,'../sensors')
from temp_sensor import TempSensor
sys.path.insert(2, '../')
import config
from wireless_module import WirelessModule
import time
import os
os.environ['PI_HOST']='127.0.0.1'
os.environ['PI_PORT']='8888'
sys.path.append('home/pi/data-acquisition-system/wireless_modules_py/sensors/Adafruit_Python_DHT/Adafruit_DHT')
import Adafruit_DHT
import logging
import asyncio

DHT_SENSOR=Adafruit_DHT.DHT22
MODULE_NUM=6

async def main():
    logging.basicConfig(
        format="%(levelname)-8s [%(filename)s] %(message)s", level=logging.DEBUG
    )

    temp_sensor_pin = config.PIN
    my_temp_sensor = TempSensor(temp_sensor_pin)

    temp_module = WirelessModule(MODULE_NUM)
    sensors = [my_temp_sensor]
    temp_module.add_sensors(sensors)

    logging.debug("Start asyncio loop")
    asyncio.create_task(temp_module.run())

    while True:
        await asyncio.sleep(1)


asyncio.run(main())
