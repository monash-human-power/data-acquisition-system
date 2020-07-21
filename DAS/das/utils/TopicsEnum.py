"""MQTT Topics for module data recording"""
from enum import Enum, unique


@unique
class NeatEnum(Enum):
    """Our base Enum class"""

    def __str__(self):
        return self.value


class WirelessModule(NeatEnum):
    """Building blocks to make a topic for a wireless module. All that is
    needed is to add a <module_id> number."""

    base = '/v3/wireless-module/'

    def battery(module_id):
        return str(WirelessModule.base) + str(module_id) + '/battery'

    def low_battery(module_id):
        return str(WirelessModule.base) + str(module_id) + '/low-battery'

    def data(module_id):
        return str(WirelessModule.base) + str(module_id) + '/data'

    def start(module_id):
        return str(WirelessModule.base) + str(module_id) + '/start'

    def stop(module_id):
        return str(WirelessModule.base) + str(module_id) + '/stop'


class WirelessModuleType(NeatEnum):
    """Used in the DataToTempCSV script to specify the type of data
    received"""

    data = "DATA"
    battery = "BATTERY"
    low_battery = "LOW_BATTERY"
