from machine import Pin, ADC
from sensor_base import Sensor


class BatteryReader(Sensor):
    def __init__(self, pin_num=33, calibration_func=lambda x: x):
        """
        Initiate the battery reader algorithm
        :param pin_num: The pin number on the ESP32 to read off the battery voltage from
        :param calibration_func: A function to transform this class's best guess at the
        battery voltage into something closer. Accepts and returns a float.
        ESP32 ADC pins)
        """
        # Resistor values in the voltage divider design here:
        # https://www.notion.so/Preliminary-Design-Report-2d0a06e271614ae886e7a2b3f88f93aa
        self.R1 = 33.2
        self.R2 = 100

        self.calibration_func = calibration_func

        self.battery_pin = Pin(pin_num)

        # Set up variables to calculate battery voltage
        self.adc_battery_pin = ADC(self.battery_pin)
        self.adc_resolution = 1024

        # Set maximum voltage readable by ADC pin to 3.6V
        self.adc_battery_pin.atten(ADC.ATTN_11DB)
        self.max_readable_voltage = 3.6

    def read(self):
        """
        Calculates the voltage of the battery attached
        :return: A dictionary containing the battery voltage
        """
        adc_value = self.adc_battery_pin.read()
        print("ADC value for the battery pin: " + str(adc_value))

        voltage_at_adc_pin = (
            self.max_readable_voltage * adc_value
        ) / self.adc_resolution
        print("Voltage at pin: " + str(voltage_at_adc_pin))

        voltageDivFactor = (self.R1 + self.R2) / self.R2
        battery_voltage = self.calibration_func(voltage_at_adc_pin * voltageDivFactor)
        print("Battery voltage calibrated: " + str(battery_voltage))

        return {"voltage": battery_voltage}


if __name__ == "__main__":
    my_battery_reader = BatteryReader()
    print(my_battery_reader.read())
