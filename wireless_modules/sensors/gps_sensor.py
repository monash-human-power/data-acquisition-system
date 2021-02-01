from machine import UART
import uasyncio as asyncio

from micropyGPS import MicropyGPS

from sensor_base import Sensor


class GpsSensor(Sensor):
    """
    A GPS sensor implementing NMEA-0183 connected via UART, such as the u-blox NEO 6M.
    """

    def __init__(self, uart_channel: int):
        """
        Begin reading data from the GPS over UART.
        :param uart_channel: The UART channel that the GPS is connected to.
        """
        self.gps = MicropyGPS(location_formatting="dd")
        asyncio.create_task(self.uart_rx(uart_channel))

    async def uart_rx(self, uart_channel: int):
        """
        Read and load data from the GPS over UART.
        """
        uart = UART(uart_channel, baudrate=9600)
        stream_reader = asyncio.StreamReader(uart)
        while True:
            res = await stream_reader.readline()
            for char in res:
                self.gps.update(chr(char))

    def read(self):
        """
        Get the most recently stored GPS data.
        :return: An array containing the GPS sensor dictionary. `value` in this
        dictionary contains spacial, quality of service and time information.
        """
        # gps.latitude[1] will be "N" if north of equator, otherwise "S" if south.
        # gps.longitude[1] is similar. The [0] component is always positive.
        latitude = self.gps.latitude[0] * (1 if self.gps.latitude[1] == "N" else -1)
        longitude = self.gps.longitude[0] * (1 if self.gps.longitude[1] == "E" else -1)
        # ISO 8601 datetime format
        datetime = "20{:02d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02.0f}".format(
            self.gps.date[2], self.gps.date[1], self.gps.date[0], *self.gps.timestamp
        )
        kph_to_mps = 1 / 3.6

        return [
            {
                "type": "gps",
                "value": {
                    "satellites": self.gps.satellites_in_use,
                    "pdop": self.gps.pdop,
                    "latitude": latitude,
                    "longitude": longitude,
                    "altitude": self.gps.altitude,
                    "speed": self.gps.speed[2] * kph_to_mps,
                    "course": self.gps.course,
                    "datetime": datetime,
                },
            }
        ]
