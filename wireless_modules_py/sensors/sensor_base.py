from abc import abstractmethod


class Sensor:
    """
    An abstract base class for all sensors.
    """

    def __init__(self):
        pass

    @abstractmethod
    def read(self):
        """
        Read the relevant sensor values and return an array of dictionaries.
        Each dictionary contains a "type" key associated with the sensor type (str) and a "value" key associated with the sensor values in any suitable format.
        """

    def on_start(self):
        """
        Perform any actions required by the sensor when the module starts publishing.
        """
