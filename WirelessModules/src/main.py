from utime import sleep
import ujson
import machine
from wireless_module import WirelessModule
from sensors.dht import DHT

module = WirelessModule()
module.add(DHT(machine.Pin(4)))

while True:
    json = ujson.dumps(module.read_sensors())
    print(json)
    sleep(1)
