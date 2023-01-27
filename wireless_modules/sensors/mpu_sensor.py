from machine import I2C
import utime
from mpu6050 import accel
from sensor_base import Sensor
from math import sqrt, atan2


class MpuSensor(Sensor):
    def __init__(self, scl_pin, sda_pin):
        """
        Initialise the MPU6050 sensor to read accelerometer and gyroscope data.
        :param scl_pin: A Pin object connected to SCL on the sensor.
        :param sda_pin: A Pin object connected to SDA on the sensor.
        :param samples: An integer representing number of readings to take the average of.
        """
        i2c = I2C(scl=scl_pin, sda=sda_pin)
        self.roll = 0
        self.pitch = 0
        self.xyz_calib_factor = {"AcX" : 1, "AcY": 1, "AcZ" : 1}
        self.xyz_calib_offset = {"AcX" : 0.0, "AcY": 0.4, "AcZ" : 0.0}
        self.accelerometer = accel(i2c)
        self.time = 0
        self.crash_detections = []

    def pitch_roll_calc(self,x,y,z):
        """
        :param x: number which represents the acceleration in the x-axis
        :param y: number which represents the acceleration in the y-axis
        :param z: number which represents the acceleration in the z-axis
        :return: a dictionary of length 2 containing values for roll and pitch calculated by roll and pitch formulas adapted from
        https://wiki.dfrobot.com/How_to_Use_a_Three-Axis_Accelerometer_for_Tilt_Sensing
        """
        values = {}
        values["roll"] = atan2(abs(round(y,1)),round(z,1)) * 57.3
        values["pitch"] = atan2(-x, sqrt(y**2 + z**2)) * 57.3 
        return values

    def read(self):
        """
        Read averaged and calibrated sensor data for the accelerometer and gyroscope.
        :param: None
        :return: An array of length 3 containing a dictionary of acceleration values, a dictionary for
                gyroscope values and a dictionary of rotation values. 
                Each contains a `type` key associated with a string of the measurement type and a
                `value` key associated with another dictionary containing (key, value) pair of the axis and it's
                relevant data.
                
                The gyroscope values are in degrees/sec ,accelerometer values are in Gs and rotation values are in degrees.
        """
        samples_per_call = 50
        lsb_to_g = 16384
        lsb_to_deg = 131
        for _ in range(samples_per_call):
            roll_average, pitch_average = 0,0 
            dt = utime.ticks_diff(utime.ticks_us(),self.time)/1000000 # calculate time step
            all_data = self.accelerometer.get_values()
            accel_values = {
                "x": (all_data["AcX"] / lsb_to_g * self.xyz_calib_factor["AcX"]) + self.xyz_calib_offset["AcX"],
                "y": (all_data["AcY"] / lsb_to_g * self.xyz_calib_factor["AcY"]) + self.xyz_calib_offset["AcY"],
                "z": (all_data["AcZ"] / lsb_to_g * self.xyz_calib_factor["AcZ"]) + self.xyz_calib_offset["AcZ"], 
            }
            gyro_values = {
                "x": all_data["GyX"] / lsb_to_deg - 14,
                "y": all_data["GyY"] / lsb_to_deg + 2.6,
                "z": all_data["GyZ"] / lsb_to_deg + 1.4,
            }
            
            ac_rotation = self.pitch_roll_calc(all_data["AcX"],all_data["AcZ"],all_data["AcY"]) # calculate angle based off acceleration values 
            gy_rotation = {"roll": self.roll + gyro_values["x"] * dt, "pitch": self.pitch + gyro_values["z"] * dt} # calculate change in angle based off gyroscope readings
            self.roll = 0.10 * ac_rotation["roll"] + 0.90 * gy_rotation["roll"] # update roll using complementary ratios
            self.pitch = 0.10 * ac_rotation["pitch"] + 0.90 * gy_rotation["pitch"] # update pitch using complementary ratios
            
            roll_average += self.roll/n
            pitch_average += self.pitch/n
            self.time = utime.ticks_us()

        rotation = {"roll":self.roll,"pitch":self.pitch} 
        return [
            {"type": "accelerometer", "value": accel_values},
            {"type": "rotation", "value": rotation},
            {"type": "gyroscope", "value": gyro_values},
        ]


    def crash_alert(self,rotation):
        """
        control flow using data from the accelerometer to determine if a crash has occurred
        :param rotation contains a dictionary of value for pitch and roll
        :return:
        """
        
        sample_crashed = False
        isCrashed = False
        if abs(rotation["pitch"]) >= 70: 
            # when bike is tipped forwards by 70 and back by 70 degrees
            sample_crashed = True
        elif abs(rotation["roll"]) >= 70:
            # when bike is tipped side to side by 70 degrees
            sample_crashed = True
        
        self.crash_detections.append(sample_crashed)
        if len(self.crash_detections) == 4:
            self.crash_detections.pop(0)
        if sum(self.crash_detections) == 3: 
            isCrashed = True
        
        return {"value": isCrashed} 
