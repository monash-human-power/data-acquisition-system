from machine import Pin
ESSID = "<WIFI NETWORK NAME HERE>"
PASSWORD = "<WIFI PASSWORD HERE>"

MQTT_BROKER = "<MQTT BROKER HERE>"

builtin_LED = Pin(2, Pin.OUT)
red_LED = Pin(13, Pin.OUT)
orange_LED = Pin(12, Pin.OUT)
green_LED = Pin(14, Pin.OUT)