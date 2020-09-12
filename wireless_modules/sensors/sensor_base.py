from abc import ABC, abstractmethod


class Sensor(ABC):
    """
    Abstract base class for all sensors
    """
    def __init__(self):
        pass

    @abstractmethod
    def read(self):
        pass
