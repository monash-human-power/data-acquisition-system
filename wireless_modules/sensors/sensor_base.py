from abc import ABC, abstractmethod


class Sensor(ABC):
    """
    Abstract base class for all sensors
    """
    def __init__(self):
        pass

    @abstractmethod
    def read(self):
        """
        Read the relevant sensor values and return an array of dictionaries for each value. Each dictionary should have
        a "type" key (associated with the name of the measurement taken in String format) and a "value" key (associated
        with the sensor values - in any format suitable).
        :return:
        """
        pass
