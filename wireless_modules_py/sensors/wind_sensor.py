from sensor_base import Sensor
import serial
import time


class WindSensor(Sensor):
    """
    A class for an anemometer connected via serial port.
    """

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
        """
        Read the wind direction (deg) and wind speed (m/s) measurements from the anemometer.
        :return: An array of length 2 containing a wind direction dictionary and a wind speed dictionary.
                 Each dictionary contains a "type" key associated with the sensor type (str) and a "value" key associated with
                 another dictionary containing key-value pairs of the measurement method (str) and its relevant data (int).
        """
        # return previous data if read() was already called less than 1 second ago
        time_since_last_read = (
            time.time_ns()*self.NS_TO_MS - self.query_time) * self.MS_TO_SEC
        if time_since_last_read < 1:
            return self.readings

        data_bytes = self.sensor.readline()
        data = data_bytes.decode('utf-8')

        # extract wind direction (deg) data
        min_direction = float(data[7:10])
        avg_direction = float(data[15:18])
        max_direction = float(data[23:26])

        # extract wind speed (m/s) data
        min_speed = float(data[31:34])
        avg_speed = float(data[39:42])
        max_speed = float(data[47:50])

        self.readings = [
            {
                "type": "windDirection",
                "value": {
                    "minDirection": min_direction,
                    "avgDirection": avg_direction,
                    "maxDirection": max_direction
                }
            },
            {
                "type": "windSpeed",
                "value": {
                    "minSpeed": min_speed,
                    "avgSpeed": avg_speed,
                    "maxSpeed": max_speed
                }
            }
        ]

        # update the last time of read() being called
        
        return self.readings
