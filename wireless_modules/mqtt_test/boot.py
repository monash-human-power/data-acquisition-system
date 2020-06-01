import config 
import esp
import network
from machine import Pin


def connect(eesid, password):
    """ Small function that continuously tries to connect to WiFi """
    
    station_interface = network.WLAN(network.STA_IF)
    if not station_interface.isconnected():
        print('connecting to network...')
        
        # Activate the WiFi interface
        station_interface.active(True)
        
        # Connect to WiFi using the credentials given
        station_interface.connect(eesid, password)

        # Loop forever until connected to WiFi    
        while not station_interface.isconnected():
            pass

    print('network config:', station_interface.ifconfig())

# Allows the code to be uploaded with tools such as rshell / ampy
esp.osdebug(None)

# Connect to WiFi using credentials stored in config.py
connect(config.ESSID, config.PASSWORD)

# Turn on the built in LED when booted and connected to WiFi (blue light)
builtin_LED = Pin(2, Pin.OUT)
builtin_LED.on()