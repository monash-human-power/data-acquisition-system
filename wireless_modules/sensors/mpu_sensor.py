from machine import I2C
from mpu6050 import accel
from sensor_base import Sensor


class MpuSensor(Sensor):
    def __init__(self, scl_pin, sda_pin, samples=10):
        """
        Initialise the MPU6050 sensor to read accelerometer and gyroscope data.
        :param scl_pin: A Pin object connected to SCL on the sensor.
        :param sda_pin: A Pin object connected to SDA on the sensor.
        :param samples: An integer representing number of readings to take the average of.
        """
        i2c = I2C(scl=scl_pin, sda=sda_pin)
        self.accelerometer = accel(i2c)
        self.calibrated_values = []
        self.samples = samples

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
            data = self.accelerometer.get_values()

            for key in data.keys():
                # Add on value / n_samples to produce an average
                # over n_samples, with default of 0 for first loop.
                result[key] = result.get(key, 0) + (data[key] / n_samples)

        if calibration:
            # Remove calibration adjustment.
            for key in calibration.keys():
                result[key] -= calibration[key]

        return result

    def calibrate(self, threshold=50, n_samples=10):
        """
        Get calibration data for the sensor, by repeatedly measuring while the sensor is stable. The resulting
        calibration dictionary contains offsets for this sensor in its current position.
        :param threshold: The accuracy of the calibration.
        :param n_samples: The number of times the sensor should be read and averaged.
        Note: Sourced from: https://www.twobitarcade.net/article/3-axis-gyro-micropython/
        """
        print("--------Calibrating:")
        while True:
            v1 = self.get_smoothed_values(n_samples)
            v2 = self.get_smoothed_values(n_samples)

            # Check all consecutive measurements are within the threshold. We use abs() so all calculated
            # differences are positive.
            if all(abs(v1[key] - v2[key]) < threshold for key in v1.keys()):
                self.calibrated_values = v1
                return v1  # Calibrated.
            print("in calibration, keep device at rest...")

    def read(self):
        """
        Read averaged and calibrated sensor data for the accelerometer and gyroscope.
        :return: An array of length 2 containing a dictionary of acceleration values and a dictionary for
                gyroscope values. Each contains a `type` key associated with a string of the measurement type and a
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

        return [
            {"type": "accelerometer", "value": accel_values},
            {"type": "gyroscope", "value": gyro_values},
        ]
