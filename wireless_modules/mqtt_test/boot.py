import config 
import esp
import network

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
config.red_LED.on()

# Connect to WiFi using credentials stored in config.py
connect(config.ESSID, config.PASSWORD)
config.red_LED.off()
config.orange_LED.on()

# Turn on the built in LED when booted and connected to WiFi (blue light)
config.builtin_LED.on()
