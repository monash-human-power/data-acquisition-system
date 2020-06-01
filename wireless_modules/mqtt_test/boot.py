from config import ESSID
from config import PASSWORD

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

def no_debug():
    import esp
    esp.osdebug(None)

# Bootup and connect to wifi credentials stored in config.py
no_debug()
connect(ESSID, PASSWORD)

# Turn on the built in LED when booted (blue light)
from machine import Pin
builtin_LED = Pin(2, Pin.OUT)
builtin_LED.on()