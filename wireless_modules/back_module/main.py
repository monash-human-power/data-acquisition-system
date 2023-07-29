import sys
import time
import uasyncio as asyncio
import machine
from wireless_module import WirelessModule
from config import STATUS_LED_PINS
from co2_sensor import CO2
from dht_sensor import DhtSensor
from gps_sensor import GpsSensor
from mpu_sensor import MpuSensor
from reed_sensor import ReedSensor
from battery_reader import BatteryReader
from status_led import StatusLed, WmState
from strain_gauge import Strain_Gauge


# Define module number
MODULE_NUM = "3"

# RZERO (for calibration of MQ135) found when the sensor was first 'activated'
# This can be found by allowing the CO2 reading to stabilise in an atmosphere
# known to be closish to 400ppm (i.e. outside) and reading the printed rzero
# on serial.
RZERO = 8.62

# Circumference of a 700x28 bike wheel in meters.
WHEEL_CIRCUMFERENCE = 2.136

# Mutable global so we can write to the LED if a fatal error occurs
status_led = StatusLed(STATUS_LED_PINS)

# Define a function to map measured voltages to "true" voltages.
# See util/battery_lin_reg.py
def battery_calibration(voltage):
    return 0.710 * voltage + 0.927


async def main():
    status_led.set_state(WmState.InitialisingSensors)
    asyncio.create_task(status_led.start_blink_loop())

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

    # Disabled in preference of ANT+ speed sensor.
    # my_reed = ReedSensor(reed_pin, WHEEL_CIRCUMFERENCE)

    my_gps = GpsSensor(2)

    my_mpu = MpuSensor(scl_pin, sda_pin)
    battery_pin = 32
    battery_reader = BatteryReader(battery_pin, battery_calibration)

    strain_gauge = Strain_Gauge(35)

    # Set up the wireless module
    back_module = WirelessModule(MODULE_NUM, battery_reader, status_led)
    sensors = [my_dht, my_mq135, my_gps, my_mpu, strain_gauge]
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
    status_led.set_warning_state(WmState.Error)

    time.sleep(5)
    machine.reset()
