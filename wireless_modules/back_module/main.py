import uasyncio as asyncio
import machine
from wireless_module import WirelessModule
from co2_sensor import CO2


# Define module number
MODULE_NUM = "3"

# RZERO (for calibration of MQ135) found when the sensor was first 'activated'
RZERO = 8.62

# Define all the Pin objects for each sensor
mq135_pin = machine.Pin(34)

# Instantiate sensor objects
my_mq135 = CO2(mq135_pin)
my_mq135.set_rzero(RZERO)

# Set up the wireless module
back_module = WirelessModule(MODULE_NUM)
sensors = [my_mq135]
back_module.add_sensors(sensors)


async def main():
    print("Starting asyncio loop")
    asyncio.create_task(back_module.run())

    while True:
        await asyncio.sleep(1)


asyncio.run(main())