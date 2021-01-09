from machine import Pin, ADC
from sensor_base import Sensor


class BatteryReader(Sensor):
    def __init__(self, pin_num=33, voltage_factor=None):
        """
        Initiate the battery reader algorithm
        :param pin_num: The pin number on the ESP32 to read off the battery voltage from
        :param voltage_factor: The factor to multiply the voltage read from the given pin to get the actual battery
        voltage (Use the voltage divider formula to find this factor)
        """
        # Resistor values in the voltage divider design here:
        # https://www.notion.so/Preliminary-Design-Report-2d0a06e271614ae886e7a2b3f88f93aa
        self.R1 = 33.2
        self.R2 = 100

        # The factor to multiply the voltage at the battery pin with to get the battery voltage
        self.voltage_factor = voltage_factor
        if voltage_factor is None:
            self.voltage_factor = (self.R1 + self.R2) / self.R1

        self.battery_pin = Pin(pin_num)

        # Set up variables to calculate battery voltage
        self.adc_battery_pin = ADC(self.battery_pin)
        self.adc_resolution = 4095

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

        voltage_at_adc_pin = (self.max_readable_voltage * adc_value) / self.adc_resolution
        print("Voltage at pin: " + str(voltage_at_adc_pin))

        battery_voltage = voltage_at_adc_pin * self.voltage_factor
        print("Battery voltage calculated: " + str(battery_voltage))

        return {
            "voltage": battery_voltage
        }


if __name__=='__main__':
    my_battery_reader = BatteryReader()
    print(my_battery_reader.read())
