import ujson
import urandom

class module:
    def __init__(self, module_num):
        """ module_num what sensors to use"""
        self.sensor = Sensor()

        # list of all of the fake sensors in each fasdfa
        if module_num == "1":
            self.sensor_lst = ["temperature", "humidity", "steering_angle"]
        
        elif module_num == "2":
            self.sensor_lst = ["co2", "temperature", "humidity", "accelerometer", "gyroscope"]
        
        elif module_num == "3":
            self.sensor_lst = ["co2", "reed_velocity", "gps"]
        
        elif module_num == "4":
            self.sensor_lst = ["power", "cadence", "heart_rate"]

                
        # Fake battery starts at 100%
        self.battery_pc = 100 

    def data(self):
        data_dict = {"sensors": []}

        for data in self.sensor_lst:
            if data == "temperature":
                data_dict["sensors"].append(self.sensor.temperature())

            elif data == "humidity":
                data_dict["sensors"].append(self.sensor.humidity())

            elif data == "steering_angle":
                data_dict["sensors"].append(self.sensor.steering_angle())

            elif data == "co2":
                data_dict["sensors"].append(self.sensor.co2())

            elif data == "accelerometer":
                data_dict["sensors"].append(self.sensor.accelerometer())
                
            elif data == "gyroscope":
                data_dict["sensors"].append(self.sensor.gyroscope())
                
            elif data == "reed_velocity":
                data_dict["sensors"].append(self.sensor.reed_velocity())
                
            elif data == "gps":
                data_dict["sensors"].append(self.sensor.gps())
                
            elif data == "power":
                data_dict["sensors"].append(self.sensor.power())
                
            elif data == "cadence":
                data_dict["sensors"].append(self.sensor.cadence())
                
            elif data == "heart_rate":
                data_dict["sensors"].append(self.sensor.heart_rate())

        return ujson.dumps(data_dict)

    def battery(self):
        """ Decrease battery % by 1 and convert to JSON string """
        self.battery_pc -= 1
        battery_dict = {"percentage": self.battery_pc}
        return ujson.dumps(battery_dict)



class Sensor:
    def temperature(self):
        return {
            "type": "temperature",
            "value": self._random_num(),
		}
    
    def humidity(self):
        return {
            "type": "humidity",
            "value": self._random_num(),
		}
    
    def steering_angle(self):
        return {
            "type": "steeringAngle",
            "value": self._random_num(),
		}

    def co2(self):
        return {
            "type": "co2",
            "value": self._random_num(),
		}

    def accelerometer(self):
        return {
            "type": "accelerometer",
            "value": {
                "x": self._random_num(),
                "y": self._random_num(),
                "z": self._random_num(),
            }
        }

    def gyroscope(self):
        return {
            "type": "gyroscope",
            "value": {
                "x": self._random_num(),
                "y": self._random_num(),
                "z": self._random_num(),
            }
        }

    def reed_velocity(self):
        return {
            "type": "reedVelocity",
            "value": self._random_num(),
        }

    def gps(self):
        return {
            "type": "gyroscope",
            "value": {
                "speed": self._random_num(),
                "satellites": self._random_num(),
                "latitude": self._random_num(),
                "longitude": self._random_num(),
                "altitude": self._random_num(),
                "course": self._random_num(),
            }
        }     

    def power(self):
        return {
            "type": "power",
            "value": self._random_num(),
        }

    def cadence(self):
        return {
            "type": "cadence",
            "value": self._random_num(),
        }

    def heart_rate(self):
        return {
            "type": "heartRate",
            "value": self._random_num(),
        } 

    def _random_num(self):
        return urandom.getrandbits(10)
