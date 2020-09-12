import dht
from sensor_base import Sensor


class DhtSensor(Sensor):
    """
    Note: The DHT22 will not be polled more than once in 2 seconds (refer to
        https://docs.micropython.org/en/latest/esp8266/tutorial/dht.html for more information). Hence new data will only
        be read every 2 seconds, and if the class is queried for data for more than this frequency, the previously read
        data will be returned instead.
    """

    def __init__(self, pin, queries=1):
        """
        Initialise the DHT sensor for temperature and humidity readings.
        :param pin: An instance of the Pin class that is connected to the DHT22 sensor.
        :param queries: Number of times the sensor will be read every 2 seconds.
        """
        self.sensor = dht.DHT22(pin)
        self.readings = []

        self.max_queries = queries
        self.queries_made = 0

    def read(self):
        """
        Read the temperature and humidity measurements from the sensor.
        :return: An array of length 2 containing dictionary for the temperature and humidity values. Each dictionary has
        a `type` key associated with the name of the sensor (a string) and a `value` key associated with the value of
        the sensor (an integer).
        """
        if self.queries_made == self.max_queries:
            self.queries_made = 0

        # read (fresh) data if this is the first query in the 2 second frame, otherwise use the previously read data
        if self.queries_made == 0:
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

        self.queries_made += 1
        return self.readings

