from machine import Pin

ESSID = "<WIFI NETWORK NAME HERE>"
PASSWORD = "<WIFI PASSWORD HERE>"

MQTT_BROKER = "192.168.100.100"

builtin_LED = Pin(2, Pin.OUT)

# Optional (Will not change the sample code)
red_LED = Pin(13, Pin.OUT)
orange_LED = Pin(12, Pin.OUT)
green_LED = Pin(14, Pin.OUT)
