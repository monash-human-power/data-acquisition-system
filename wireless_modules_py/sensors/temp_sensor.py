from sensor_base import Sensor
import time
import sys
import Adafruit_DHT
class TempSensor(Sensor):
    """
    A class for the DHT_22 temp sensor
    """
    def __init__(self, pin):
        """
        Getting the DHT_22 temp sensor and pin for readings
        """
        self.pin=pin
        self.sensor=Adafruit_DHT.DHT22

    def read(self):
        """
        Read the temperature (deg in Cel) and humidity (%) from the temperature sensor
        :return: An array of length 2 containing a temperature dictionary and a humidity dictionary.
                 Each dictionary contains a "type" key associated with the sensor type (str) and a "value" key associated with
                 another dictionary containing key-value pairs of the measurement method (str) and its relevant data (float).
        """
        readings=[]
        humidity, temperature=Adafruit_DHT.read_retry(self.sensor,self.pin)
        if humidity is not None and temperature is not None:
            temperature=round(float(temperature),2)
            humidity=round(float(humidity),2)
            readings = [
                {
                "temp_in_deg": temperature,
                },
                {
                "humidity_in_percent": humidity,
                }
                ] 
        else:
            print('Failed to obtain data')
        return readings
