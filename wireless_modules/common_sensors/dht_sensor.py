# Class for the DHT22 sensor
import dht


class DhtSensor:
    def __init__(self, pin):
        """
        Initialise the DHT sensor
        :param pin: A Pin object
        """
        self.sensor = dht.DHT22(pin)

        # Variable to ensure data is read only once per second
        self.read_already = False
        self.readings = []

    def read(self):
        """
        Reads the temperature and humidity measurements from the sensor and returns it as an array of dictionaries
        :return: An array of length 2 containing dictionary for teh temperature and humidity data
        """
        if self.read_already:
            self.read_already = False
        else:
            self.sensor.measure()
            self.readings = [{
                                "type": "temperature",
                                "value": self.sensor.temperature()
                             },
                            {
                                "type": "humidity",
                                "value": self.sensor.humidity()
                            }]
            self.read_already = True

        return self.readings

