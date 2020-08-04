# Author: Kunj
# Last updated: 1/08/2020

# Import relevant libraries
import esp
import network
import config
import time


def do_connect(essid, password):
    """
    Tries to connect to the WIFI 5 times at max
    :param essid: The WIFI name to connect to, ensure it's not in double quotes but single ones
    :param password: The WIFI password to connect, ensure it's not in double quotes but single quotes
    :return: None
    """

    max_wifi_attempts = 5

    # Create station interface
    station_interface = network.WLAN(network.STA_IF)
    station_interface.active(True)

    if station_interface.isconnected():
        print('network config:', station_interface.ifconfig())

        # Turn on the built in LED when booted and connected to WiFi (blue light)
        config.builtin_LED.on()
        time.sleep(5)
        config.builtin_LED.off()
    else:
        print('connecting to network...')

        while not station_interface.isconnected() and max_wifi_attempts > 0:
            # Connect to WiFi using the credentials given
            station_interface.connect(essid, password)

            if not station_interface.isconnected():
                print('Could not connect to WIFI, attempts:', max_wifi_attempts)
            else:
                print('Connected, network config:', station_interface.ifconfig())

            attempts = attempts - 1


esp.osdebug(None)
# connect to WIFI
do_connect(config.ESSID, config.PASSWORD)





