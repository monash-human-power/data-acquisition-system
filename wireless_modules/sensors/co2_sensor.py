from MQ135 import MQ135
from sensor_base import Sensor
from machine import ADC


class CO2(Sensor):
    def __init__(self, pin):
        """
        A MQ135 sensor class to read co2 concentration levels.
        :param pin: An instance of the machine.Pin class connected to the MQ135 class.
        """
        # Change ADC resolution to 10 bits consistent with the ESP8266 in order to use the MQ135 library
        adc = ADC(pin)
        adc.width(ADC.WIDTH_10BIT)

        self.mq135 = MQ135(pin)
        self.dht = None
        self.temperature = None
        self.humidity = None
        self.dht_sensor_provided = False

    def set_dht(self, dht_instance):
        """
        Provide the dht sensor to automatically read the temperature and humidity values to get a more accurate co2
        concentration reading when the read() method is called.
        :param dht_instance: An instance of the dht class (Must contain a .read() method).
        """
        self.dht = dht_instance
        self.dht_sensor_provided = True

    def set_temp_humidity(self, temp, humidity):
        """
        Set the temperature and humidity measurement manually, used to get more accurate co2 concentration readings.
        If a dht class instance is also provided, that class will be used instead to get temperature and humidity.
        :param temp: An integer representing temperature in degree Celsius.
        :param humidity: An integer representing humidity.
        """
        self.temperature = temp
        self.humidity = humidity

    def _read_temp_humidity(self):
        """
        Read temperature and humidity data from the dht sensor if provided.
        """
        if self.dht_sensor_provided:
            data = self.dht.read()
            self.temperature = data[0]["value"]
            self.humidity = data[1]["value"]

    def get_rzero(self):
        """
        Read RZERO value from the MQ135 library.
        :return: An integer representing the calibration resistance at atmospheric CO2 level.
        """
        self._read_temp_humidity()

        if self.temperature is not None:
            return self.mq135.get_corrected_rzero(self.temperature, self.humidity)
        else:
            return self.mq135.get_rzero()

    def set_rzero(self, rzero):
        """
        Set the RZERO value in the MQ135 library.
        :param rzero: An integer representing the Calibration resistance at atmospheric CO2 level.
        """
        self.mq135.RZERO = rzero

    def read(self):
        """
        Read the co2 concentration level. It uses the temperature and humidity data to get a more 'correct' reading, if
        provided.
        Assume only co2 in the air.
        :return: An array of length 1 containing a dictionary with the sensor type (string) and sensor value (int). The
        sensor value is in PPM.
        """
        self._read_temp_humidity()

        # If the MQ135 is not heated up, the method to extract PPM will crash with a ValueError
        try:
            if self.temperature is not None:
                ppm = self.mq135.get_corrected_ppm(self.temperature, self.humidity)

                print("\t MQ135 Corrected PPM: " + str(ppm))

            else:
                ppm = self.mq135.get_ppm()

                print("\t MQ135 PPM: " + str(ppm) + "\t rzero: " + str(self.mq135.get_rzero()))
        except ValueError:
            # Since ppm cannot reasonably be 0, this can be used to mark that the sensor has not yet heated up
            ppm = 0

        return [{
            "type": "co2",
            "value": ppm
        }]
