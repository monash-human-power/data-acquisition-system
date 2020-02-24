"""MQTT Topics for Camera System"""
from enum import Enum, unique


@unique
class NeatEnum(Enum):
    """Our base Enum class"""

    def __str__(self):
        return self.value
