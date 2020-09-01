import dht


class DhtSensor:
    def __init__(self, pin, queries=2):
        """
        Initialise the DHT sensor
        :param pin: A Pin object
        :param queries: Number of times the sensor will be read every 2 seconds
        """
        self.sensor = dht.DHT22(pin)
        self.readings = []

        self.max_queries = queries
        self.queries_made = 0

    def read(self):
        """
        Reads the temperature and humidity measurements from the sensor and returns it as an array of dictionaries
        :return: An array of length 2 containing dictionary for the temperature and humidity values
        """
        if self.queries_made == self.max_queries:
            self.queries_made = 0

        # read (fresh) data if this if the first query in the 2 second frame, otherwise return previously read data
        if self.queries_made == 0:
            self.sensor.measure()
            self.readings = [{
                                "type": "temperature",
                                "value": self.sensor.temperature()
                             }, {
                                "type": "humidity",
                                "value": self.sensor.humidity()
                            }]

        self.queries_made += 1
        return self.readings

