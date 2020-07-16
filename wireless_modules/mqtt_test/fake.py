import ujson
import urandom

class module:
    def __init__(self, module_num):
        """ Mimics the real wireless modules on V3 """

        # Hardcoded sensors that are in each wireless module on the bike
        MODULE_SENSORS = {
            "1": ["temperature", "humidity", "steeringAngle"],
            "2": ["co2", "temperature", "humidity", "accelerometer", "gyroscope"],
            "3": ["co2", "reedVelocity", "gps"],
            "4": ["power", "cadence", "heartRate"],
        }

        # Select the correct module config
        self.sensor_lst = MODULE_SENSORS[module_num]

        # Fake battery starts at 100%
        self.battery_pc = 100 

    def data(self):
        # Dictionary to store the randomly generated data (to be sent over MQTT)
        data_dict = {"sensors": []}

        for sensor_name in self.sensor_lst:
            if sensor_name == "gps":
                fake_data = FakeSensor(sensor_name).value_GPS()

            elif sensor_name == "accelerometer" or sensor_name == "gyroscope":
                fake_data = FakeSensor(sensor_name).value_xyz()

            else:
                fake_data = FakeSensor(sensor_name).value_single()

            data_dict["sensors"].append(fake_data)

        return ujson.dumps(data_dict)

    def battery(self):
        """ Decrease battery % by 1 and convert to JSON string """
        
        self.battery_pc -= 1
        battery_dict = {"percentage": self.battery_pc}
        return ujson.dumps(battery_dict)


class FakeSensor:
    def __init__(self, sensor_name):
        """ Takes a sensor_name to be used in the output data dict """
        self.sensor_name = sensor_name

    def value_single(self):
        """ Returns fake simple (only value) data for the given 
        self.sensor_name """
        return {
            "type": str(self.sensor_name),
            "value": self._random_num(),
        }

    def value_xyz(self):
        """ Returns fake xyz data for the given self.sensor_name """
        return {
            "type": str(self.sensor_name),
            "value": {
                "x": self._random_num(),
                "y": self._random_num(),
                "z": self._random_num(),
            }
        }

    def value_GPS(self):
        """ Returns fake GPS data for the given self.sensor_name """
        return {
            "type": str(self.sensor_name),
            "value": {
                "speed": self._random_num(),
                "satellites": self._random_num(),
                "latitude": self._random_num(),
                "longitude": self._random_num(),
                "altitude": self._random_num(),
                "course": self._random_num(),
            }
        }     

    def _random_num(self):
        """ Generates a pseudo-random number """
        return urandom.getrandbits(10)
