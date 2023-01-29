from abc import abstractmethod


class Sensor:
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

    def on_start(self):
        """
        Performs any actions required by the sensor when the module starts publishing.
        """
