"""MQTT Topics for module data recording"""
from enum import Enum, unique


@unique
class NeatEnum(Enum):
    """Our base Enum class"""

    def __str__(self):
        return self.value


class WirelessModuleData(NeatEnum):
    """Topics for sending data over MQTT"""
    module_1 = '/v3/wireless-module/1/data'
    module_2 = '/v3/wireless-module/2/data'
    module_3 = '/v3/wireless-module/3/data'
    module_4 = '/v3/wireless-module/4/data'


class WirelessModuleBattery(NeatEnum):
    """Topics for sending battery information over MQTT"""
    module_1 = '/v3/wireless-module/1/battery'
    module_2 = '/v3/wireless-module/2/battery'
    module_3 = '/v3/wireless-module/3/battery'
    module_4 = '/v3/wireless-module/4/battery'


class WirelessModuleStart(NeatEnum):
    """Topics for starting the data recording"""
    module_1 = '/v3/wireless-module/1/start'
    module_2 = '/v3/wireless-module/2/start'
    module_3 = '/v3/wireless-module/3/start'
    module_4 = '/v3/wireless-module/4/start'


class WirelessModuleStop(NeatEnum):
    """Topics for stopping the data recording"""
    module_1 = '/v3/wireless-module/1/stop'
    module_2 = '/v3/wireless-module/2/stop'
    module_3 = '/v3/wireless-module/3/stop'
    module_4 = '/v3/wireless-module/4/stop'
