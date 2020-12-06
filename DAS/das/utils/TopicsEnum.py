"""MQTT Topics for module data recording"""
from enum import Enum, unique


@unique
class NeatEnum(Enum):
    """Our base Enum class"""

    def __str__(self):
        return self.value


class WirelessModuleType(NeatEnum):
    """Used in the DataToTempCSV script to specify the type of data
    received"""

    data = "DATA"
    battery = "BATTERY"
    low_battery = "LOW_BATTERY"
