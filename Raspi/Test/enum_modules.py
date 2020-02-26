"""MQTT Topics for module data recording"""
from enum import Enum, unique
from MockSensor import MockSensor


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
        return '/v3/wireless-module/' + str(module_id) + '/battery'

    def low_battery(module_id):
        return '/v3/wireless-module/' + str(module_id) + '/low-battery'

    def data(module_id):
        return '/v3/wireless-module/' + str(module_id) + '/data'

    def start(module_id):
        return '/v3/wireless-module/' + str(module_id) + '/start'

    def stop(module_id):
        return '/v3/wireless-module/' + str(module_id) + '/stop'

s_steering_angle = MockSensor(10)
s_co2 = MockSensor(325)
s_temperature = MockSensor(25)
s_humidity = MockSensor(85)
s_reed_velocity = MockSensor(50)
s_battery = MockSensor(80)
s_accelerometer = MockSensor(("x", 90),
                             ("y", 90),
                             ("z", 90))
s_gyroscope = MockSensor(("x", 90),
                         ("y", 90),
                         ("z", 90))
s_gps = MockSensor(("speed", 50),
                   ("satellites", 10),
                   ("latitude", 25),
                   ("longitude", 25),
                   ("altitude", 50),
                   ("course", 0))
