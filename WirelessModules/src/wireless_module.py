class WirelessModule:
    def __init__(self):
        super().__init__()
        self.sensors = []

    def add(self, sensor):
        self.sensors.append(sensor)
    
    def read_sensors(self):
        readings = []
        for sensor in self.sensors:
            readings += sensor.read()
        return readings
