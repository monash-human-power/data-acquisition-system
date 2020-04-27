from dht import DHT22
from sensors.base import Sensor

class DHT(Sensor):
    def __init__(self, pin):
        super().__init__()
        self.dht = DHT22(pin)

    def read(self):
        self.dht.measure()
        return (
            {
                'type': 'temperature',
                'value': self.dht.temperature(),
            },
            {
                'type': 'humidity',
                'value': self.dht.humidity(),
            },
        )
