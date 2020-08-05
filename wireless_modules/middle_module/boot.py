
import esp
import network
import config


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

    while not station_interface.isconnected() and max_wifi_attempts > 0:
        # Connect to WiFi using the credentials given
        station_interface.connect(essid, password)

        if not station_interface.isconnected():
            print("Could not connect to WIFI, attempts:", max_wifi_attempts)
        else:
            print("Connected, network config:", station_interface.ifconfig())
            # Turn on the built in LED when booted and connected to WiFi (blue light)
            config.builtin_LED.on()

        max_wifi_attempts = max_wifi_attempts - 1


esp.osdebug(None)
# connect to WIFI
do_connect(config.ESSID, config.PASSWORD)
