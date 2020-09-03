
from MQ135 import MQ135


class co2:
    def __init__(self, pin):
        """
        A MQ135 sensor class to read co2 concentration levels
        :param pin: An object of the machine.Pin class
        """
        self.mq135 = MQ135(pin)
        self.dht = None
        self.temperature = None
        self.humidity = None
        self.dht_sensor_provided = False

    def set_dht(self, dht_instance):
        """
        Provides the dht sensor to automatically read the temperature and humidity values to get a more accurate co2
        concentration reading.
        :param dht_instance: An instance of the dht class (Must contain a .read() method)
        """
        self.dht = dht_instance
        self.dht_sensor_provided = True

    def set_temp_humidity(self, temp, humidity):
        """
        Sets the temperature and humidity measurement manually, used to get a more accurate co2 concentration reading.
        If a dht class instance is also provided, that class be used instead to get the temperature and humidity.
        :param temp: An integer representing temperature in degree Celsius
        :param humidity: An integer representing humidity
        """
        self.temperature = temp
        self.humidity = humidity

    def _read_temp_humidity(self):
        """
        To read temperature and humidity data from the dht sensor if provided.
        """
        if self.dht_sensor_provided:
            data = self.dht.read()
            self.temperature = data[0]["value"]
            self.humidity = data[1]["value"]

    def get_rzero(self):
        """
        Reads the rzero value from the library
        :return: An integer representing the calibration resistance at atmospheric CO2 level
        """
        self._read_temp_humidity()

        if self.temperature is not None:
            return self.mq135.get_corrected_rzero(self.temperature, self.humidity)
        else:
            return self.mq135.get_rzero()

    def set_rzero(self, rzero):
        """
        Sets the Rzero value in the library code used for the MQ135 sensor
        :param rzero: An integer representing the Calibration resistance at atmospheric CO2 level
        :return:
        """
        self.mq135.RZERO = rzero

    def read(self):
        """
        Reads the co2 concentration level. It uses the temperature and humidity data to get a more 'correct' reading, if
        provided.
        Assumes only co2 in the air.
        :return: An array of length 1 containing a dictionary with the sensor type (string) and sensor value (int)
        """
        self._read_temp_humidity()

        if self.temperature is not None:
            corrected_rzero = self.mq135.get_corrected_rzero(self.temperature, self.humidity)
            ppm = self.mq135.get_corrected_ppm(self.temperature, self.humidity)

            print("MQ135 Corrected RZero: " + str(corrected_rzero) + "\t Corrected PPM: " + str(ppm) + "ppm")

        else:
            rzero = self.mq135.get_rzero()
            ppm = self.mq135.get_ppm()

            print("MQ135 RZero: " + str(rzero) + "\t PPM: " + str(ppm))

        return [{
            "type": "co2",
            "value": ppm
        }]

