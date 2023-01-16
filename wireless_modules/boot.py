import esp
import network
from machine import Pin

import config
from status_led import StatusLed, WmState


def do_connect(essid, password):
    """
    Continuously tries to connect to the WIFI
    :param essid: The WIFI name to connect to, in string format
    :param password: The WIFI password to connect, in string format
    :return: Nothing
    """
    print("Attempting to connect to WIFI")
    # Create station interface
    station_interface = network.WLAN(network.STA_IF)
    station_interface.active(True)

    # Connect to WiFi
    station_interface.connect(essid, password)

    # Wait for the module to connect
    while not station_interface.isconnected():
        pass

    print("Connected, network config:", station_interface.ifconfig())


status_led = StatusLed(config.STATUS_LED_PINS)
status_led.set_state(WmState.ConnectingToNetwork)

# Allows the code to be uploaded with tools such as rshell / ampy
esp.osdebug(None)
do_connect(config.ESSID, config.PASSWORD)

# Turn on the built in LED when booted and connected to WiFi (blue light)
builtin_led = Pin(config.BUILTIN_LED_PIN, Pin.OUT)
builtin_led.on()
