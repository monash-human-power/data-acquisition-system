
import esp
import network
import config


def do_connect(essid, password):
    """
    Countinously tries to connect to the WIFI
    :param essid: The WIFI name to connect to, ensure it's not in double quotes but single ones
    :param password: The WIFI password to connect
    :return: Nothing
    """

    # Create station interface
    station_interface = network.WLAN(network.STA_IF)
    station_interface.active(True)

    # Connect to WiFi using the credentials given
    station_interface.connect(essid, password)

    # Wait for the module to connect
    while not station_interface.isconnected(): 
        pass
    
    print("Connected, network config:", station_interface.ifconfig())
    # Turn on the built in LED when booted and connected to WiFi (blue light)
    config.builtin_LED.on()


esp.osdebug(None)
do_connect(config.ESSID, config.PASSWORD)
