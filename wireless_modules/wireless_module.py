"""
A class structure to read and format/collate data from different sensors into a dictionary
"""


class WirelessModule:
    def __init__(self):
        self.sensors = []

    def add(self, sensor_obj):
        """
        Store an instance of a sensor class
        :param sensor_obj: An instance of the sensor class, must have a .read() method to read data
        """
        self.sensors.append(sensor_obj)

    def read_sensors(self):
        """
        Reads sensor data from each sensor object stored within this class
        :return: A dictionary of all the sensor types and they're corresponding sensor reading/s
        :pre-requisite: The read() method for each sensor must return an object
        """
        readings = {"sensors": []}

        for sensor in self.sensors:
            sensor_data = sensor.read()
            for data in sensor_data:
                readings["sensors"].append(data)

        return readings

