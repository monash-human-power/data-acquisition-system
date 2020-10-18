import dht
import time
from sensor_base import Sensor


class DhtSensor(Sensor):
    """
    Note: The DHT22 will not be polled more than once in 2 seconds (refer to
        https://docs.micropython.org/en/latest/esp8266/tutorial/dht.html for more information). Hence new data will only
        be read every 2 seconds, and if the class is queried for more than this frequency, the previously read
        data will be returned instead.
    """

    def __init__(self, pin):
        """
        Initialise the DHT sensor for temperature and humidity readings.
        :param pin: An instance of the Pin class that is connected to the DHT22 sensor.
        """
        self.sensor = dht.DHT22(pin)
        self.readings = []

        self.query_time = 0  # To track frequency at which the read() method is called
        self.MS_TO_SEC = 1/1000

    def read(self):
        """
        Read the temperature and humidity measurements from the sensor.
        :return: An array of length 2 containing dictionary for the temperature and humidity values. Each dictionary has
        a `type` key associated with the name of the sensor (a string) and a `value` key associated with the value of
        the sensor (an integer).
        The temperature measurement is in Degrees Celsius and Humidity measurement is in relative %.
        """

        # Return old data if this method was called already in the past 2 seconds
        time_since_last_read = time.ticks_diff(time.ticks_ms(), self.query_time) * self.MS_TO_SEC
        if time_since_last_read < 2:
            return self.readings

        self.sensor.measure()
        self.readings = [
            {
                "type": "temperature",
                "value": self.sensor.temperature()
            },
            {
                "type": "humidity",
                "value": self.sensor.humidity()
            }
        ]
        self.query_time = time.ticks_ms()
        return self.readings

