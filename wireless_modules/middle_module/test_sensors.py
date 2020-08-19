from wireless_module import WirelessModule
from mpu import Mpu
from dht_sensor import DhtSensor
from machine import Pin
import time


class SensorTest:
    def __init__(self, pin_scl, pin_sda, pin_dht):
        """
        Initialises all sensors
        :param pin_scl: A Pin object for the SCL connection of the MPU6050 sensor
        :param pin_sda: A Pin object for the SDA connection of the MPU6050 sensor
        :param pin_dht: A Pin object for the DHT22 sensor
        """
        print("Initialising all sensors")
        mpu = Mpu(pin_scl, pin_sda)
        dht = DhtSensor(pin_dht)

        self.module = WirelessModule()
        self.module.add(mpu)
        self.module.add(dht)

    def read_all_sensors(self):
        return self.module.read_sensors()


test = SensorTest(Pin(22), Pin(21), Pin(4))
print("printing sensor values")
while True:
    readings = test.read_all_sensors()
    for data in readings["sensors"]:
        print(data["type"], "\t", data["value"])
    # print(readings["sensors"][0]["type"], "\t ", readings["sensors"][0]["value"])
    # print(readings["sensors"][1]["type"], "\t ", readings["sensors"][1]["value"])
    # print(readings["sensors"][2]["type"], "\t\t ", readings["sensors"][2]["value"])
    # print(readings["sensors"][2]["type"], "\t\t ", readings["sensors"][2]["value"])
    print("\n")
    time.sleep(2)
