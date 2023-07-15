from machine import ADC, Pin
from sensor_base import Sensor

ALPHA = 0.2
VREF = 3.3
ATTENUATION = 4095.0

class Strain_Gauge(Sensor):
    def __init__(self,pin) -> None:
        self.gain = 100 # amplifier gain
        self.ratio = 0.5 # bridge ratio
        self.voff = 3.3/2
        self.pin = pin
        self.strain = 0
        pass

    def read_analog(self):
        adc = ADC(Pin(self.pin))
        adc.read() /ATTENUATION * VREF
        
    
    def ema_filter(current_value, previous_value):
        """
        Exponential moving average filter reduces potency of incoming fluctuation or noise
        :param current_value: The incoming value in a new time step
        :param previous_value: A stored value from the last time step
        :return filtered_value: An adjusted value that to take the place of current_value
        """
        filtered_value = ALPHA * current_value + (1-ALPHA) * previous_value
        return filtered_value 
    
    def read(self):
        differential_voltage = self.read_analog() - self.voff        
        strain = differential_voltage/(self.gain * VREF * self.ratio)
        filtered_strain = self.ema_filter(strain,self.strain,self.alpha)
        self.strain = filtered_strain
        return filtered_strain