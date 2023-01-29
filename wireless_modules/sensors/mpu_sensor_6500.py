from machine import I2C
# from mpu6050 import accel
from math import atan2, sqrt
from mpu6500 import MPU6500
from sensor_base import Sensor

class MpuSensor(Sensor):
    def __init__(self, scl_pin, sda_pin, samples=10, rolling_samples=5):
        """
        Initialise the MPU6050 sensor to read accelerometer and gyroscope data.
        :param scl_pin: A Pin object connected to SCL on the sensor.
        :param sda_pin: A Pin object connected to SDA on the sensor.
        :param samples: An integer representing number of readings to take the average of.
        """
        i2c = I2C(scl=scl_pin, sda=sda_pin)
        self.accelerometer = MPU6500(i2c)
        self.calibrated_values = []
        self.samples = samples
        self.rolling_samples = rolling_samples
        self.rolling_accel= []
        self.normal = ""

    def get_values_as_dict(self):
        """
        mpu6500 helper module seperates accelerometer, gyroscope and temperature data into
        3 different properties. This function is used to concatenate all values into a dictionary
        to be used in pre-existing get_smoothed_values method. 

        """
        values = {}
        values["acx"], values["acy"], values["acz"] = self.accelerometer.acceleration()
        values["temp"] = self.accelerometer.temperature()
        values["gyx"], values["gyy"], values["gyz"] = self.accelerometer.gyro()
        return values

    def get_smoothed_values(self, n_samples=10, calibration=None):
        """
        Get smoothed values from the sensor by sampling
        the sensor `n_samples` times and returning the mean.

        If passed a `calibration` dictionary, subtract these
        values from the final sensor value before returning.
        :param n_samples: The number of samples to take average from
        :param calibration: calibration values to offset by
        :return: A dictionary of mean sensor measurements for the temperature, 3 dimensions of acceleration and
                gyroscope
        Note: Sourced from https://www.twobitarcade.net/article/3-axis-gyro-micropython/
        """
        result = {}
        for _ in range(n_samples):
            data = self.get_values_as_dict()
            for key in data.keys():
                result[key] += result.get(key,0) + (data[key]/n_samples)

        # if calibration:
        #     # Remove calibration adjustment.
        #     for key in calibration.keys():
        #         result[key] -= calibration[key]

        return result

    def roll_calc(y,z):
        """
        calculates the roll angle of the bike using the y-axis acceleration and z-axis acceleration
        in this case: 
        y-axis acceleration is perpendicular to direction of travel
        z-axis acceleration is normal to the ground
        it is used to determine if the bike is on its sides.


        ########################################################################
        need to test if rest give positive vertical axis readings
        #########################################################################
        """
        return atan2(y,z) * 57.3

    def pitch_calc(x,y,z):
        return atan2((- x) , sqrt(y * y + z * z)) * 57.3;

    def get_max_accel(self, accel_values):
        """
        Get the index of the maximum acceleration value from the acceleration dictionary and return
        the key to that value.
        :param: The acceleration value dictionary
        """
        v = list(accel_values.values())
        k = list(accel_values.keys())
        max_val = max(v, key=abs)
        return [k[v.index(max_val)], abs(max_val)]

    def get_mode_list(self, List):
        return max(set(List), key = List.count)

    def read(self, crash_only = False):
        """
        Read averaged and calibrated sensor data for the accelerometer and gyroscope.
        :param crash_only: If True, function will only return the crash detection data.
        :return: An array of length 3 containing a dictionary of acceleration values, a dictionary for
                gyroscope values and a boolean if there has been a crash detected. 
                Each contains a `type` key associated with a string of the measurement type and a
                `value` key associated with another dictionary containing (key, value) pair of the axis and it's
                relevant data.
                
                The gyroscope values are in degrees/sec and accelerometer values are in Gs.
        """
        lsb_to_g = 16384
        lsb_to_deg = 131
        all_data = self.get_smoothed_values(
            n_samples=self.samples, calibration=self.calibrated_values
        )
        accel_values = {
            "x": all_data["AcX"] / lsb_to_g,
            "y": all_data["AcY"] / lsb_to_g,
            "z": all_data["AcZ"] / lsb_to_g,
        }
        gyro_values = {
            "x": all_data["GyX"] / lsb_to_deg,
            "y": all_data["GyY"] / lsb_to_deg,
            "z": all_data["GyZ"] / lsb_to_deg,
        }
        if len(self.rolling_accel) == self.rolling_samples-1:
            self.normal = self.get_mode_list(self.rolling_accel)
        if len(self.rolling_accel) < self.rolling_samples:
            self.rolling_accel.append(self.get_max_accel(accel_values)[0])
        else:
            self.rolling_accel.pop(0)
            self.rolling_accel.append(self.get_max_accel(accel_values)[0])

        isCrashed = False
        if (len(self.rolling_accel) == self.rolling_samples):
            if (self.get_mode_list(self.rolling_accel) != self.normal):
                isCrashed = True
            

        if not crash_only:
            return [
                {"type": "accelerometer", "value": accel_values},
                {"type": "gyroscope", "value": gyro_values},
                {"type": "crashed", "values": isCrashed}
            ]
        else:
            return [{"type": "crashed", "values": isCrashed}]


    ##################################################################
    # Need to implement seperate method? one for crash alerts and one for data
    # Outputs to two different topics: crashes and acceleration data
    ##################################################################

    """
    Things to work on:
    1. mpu6500 module performs calculations to convert raw readings to SI units 
    on every read. Implement method to perfrom conversion later on to reduce number
    of operations.

    2. 

    """
    def read(self):
        
    def crash_check(self,roll):
        if roll > 30 and roll < 330:
            return [{"type": "crashed", "values": True}]
        else: 
            return [{"type": "crashed", "values": False}]

        
        

