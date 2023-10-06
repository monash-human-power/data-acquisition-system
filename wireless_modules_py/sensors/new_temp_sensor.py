from sensor_base import Sensor
import serial
import time
import Adafruit_DHT as dht
class Temp_sensor(Sensor):
    def __init__(self, port):
        """
        Initialise the anemometer to read wind direction and wind speed data.
        :param port: The serial port that the anemometer is connected to.
        """
        self.baudrate = 19200
        self.sensor = serial.Serial(port, self.baudrate)

        self.readings = []

        self.query_time = 0
        self.MS_TO_SEC = 1/1000
        self.NS_TO_MS = 1000000
    def read(self):
        self.sensor()