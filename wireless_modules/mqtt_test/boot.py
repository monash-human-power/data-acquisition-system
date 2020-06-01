from config import ESSID
from config import PASSWORD
from machine import Pin
import esp

def connect(eesid, password):
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(eesid, password)
        while not sta_if.isconnected():
            pass

    print('network config:', sta_if.ifconfig())

# Allows the code to be uploaded with tools such as rshell / ampy
esp.osdebug(None)

# Connect to WiFi using credentials stored in config.py
connect(ESSID, PASSWORD)

# Turn on the built in LED when booted and connected to WiFi (blue light)
builtin_LED = Pin(2, Pin.OUT)
builtin_LED.on()