from sensor_base import Sensor
import serial
import smbus
import numpy as np
import time

class PressureSensor(Sensor):
    """
    A class for a barometer connected via serial port.
    """

    def __init__(self, port):
        """
        Initialise the Barometer to read air pressure, temperature and altitude.
        :param port: The i2c address that the barometer is connected to.
        """
        self.i2c_address = port
        self.i2c_ch = 1
        self.readings = []
        self.get_coefficients()
        self.query_time = 0
        self.MS_TO_SEC = 1/1000
        self.NS_TO_MS = 1000000


    def read(self):
        
        """
        Read the air pressure (Pa), temperature (C) and altitude (m) measurements from the barometer.
        :return: An array of length 3 containing a dictionary for each meausurement
                 Each dictionary contains a "type" key associated with the data type (str) and a "value" key associated with the value.
        """
        # return previous data if read() was already called less than 1 second ago
        time_since_last_read = (
            time.time_ns()*self.NS_TO_MS - self.query_time) * self.MS_TO_SEC
        if time_since_last_read < 1:
            return self.readings


        temperature = self.get_temp() #C
        pressure = self.get_pressure()  #Pa
        altitude = self.get_altitude(pressure) #m

        self.readings = [
            {
                "type": "temperature",
                "value": temperature
            },
            {
                "type": "airPressure",
                "value": pressure
                
            },
            {
                "type": "altitude",
                "value": altitude
            }
        ]

        
        
        # update the last time of read() being called
        self.query_time = time.time_ns() * self.NS_TO_MS

        return self.readings
    
    
    
    def get_altitude(self, air_pressure):
        
        P0 = 1013.25 #this might need to be calculated for melbourne/clayton idk
        altitude = 44330 * (1-pow(air_pressure/P0,1/5.255))
        return altitude
        
    def get_temp(self):
        traw_sc = self.get_traw_sc()
        temp_c = ((self.c0) * 0.5) + ((self.c1) * traw_sc)
        return temp_c
    
    def get_pressure(self):
        traw_sc = self.get_traw_sc()
        praw_sc = self.get_praw_sc()
        p_comp = self.c00 + praw_sc*(self.c10+ praw_sc*(self.c20+ praw_sc*self.c30)) + traw_sc*self.c01 + traw_sc*praw_sc*(self.c11+praw_sc*self.c21)
        return p_comp
         
    def get_traw_sc(self):
        traw_sc = self.get_traw()/self.get_temperature_scale_factor()
        return traw_sc
    
    def get_praw_sc(self):
        praw_sc = self.get_praw()/self.get_pressure_scale_factor()
        return praw_sc
        
    def get_traw(self):
        tmp_MSB = bus.read_byte_data(self.i2c_address, 0x03)
        tmp_LSB = bus.read_byte_data(self.i2c_address, 0x04)
        tmp_XLSB = bus.read_byte_data(self.i2c_address, 0x05)

        tmp = np.uint32(tmp_MSB << 16) | np.uint32(tmp_LSB << 8) | np.uint32(tmp_XLSB)

        if(tmp & (1 << 23)):
            tmp = tmp | 0XFF000000

        return np.int32(tmp)
    
    def get_praw(self):
        tmp_MSB = bus.read_byte_data(self.i2c_address, 0x00)
        tmp_LSB = bus.read_byte_data(self.i2c_address, 0x01)
        tmp_XLSB = bus.read_byte_data(self.i2c_address, 0x02)

        tmp = np.uint32(tmp_MSB << 16) | np.uint32(tmp_LSB << 8) | np.uint32(tmp_XLSB)

        if(tmp & (1 << 23)):
            tmp = tmp | 0XFF000000

        return np.int32(tmp)
    
    def get_temperature_scale_factor(self):
        tmp_Byte = bus.read_byte_data(self.i2c_address, 0x07)

        tmp_Byte = tmp_Byte & 0B111

        if(tmp_Byte == 0B000):
            k = 524288.0

        if(tmp_Byte == 0B001):
            k = 1572864.0

        if(tmp_Byte == 0B010):
            k = 3670016.0

        if(tmp_Byte == 0B011):
            k = 7864320.0

        if(tmp_Byte == 0B100):
            k = 253952.0

        if(tmp_Byte == 0B101):
            k = 516096.0

        if(tmp_Byte == 0B110):
            k = 1040384.0

        if(tmp_Byte == 0B111):
            k = 2088960.0 

        return k
    
    def get_pressure_scale_factor(self):
        tmp_Byte = bus.read_byte_data(self.i2c_address, 0x06)

        tmp_Byte = tmp_Byte & 0B111

        if(tmp_Byte == 0B000):
            k = 524288.0

        if(tmp_Byte == 0B001):
            k = 1572864.0

        if(tmp_Byte == 0B010):
            k = 3670016.0

        if(tmp_Byte == 0B011):
            k = 7864320.0

        if(tmp_Byte == 0B100):
            k = 253952.0

        if(tmp_Byte == 0B101):
            k = 516096.0

        if(tmp_Byte == 0B110):
            k = 1040384.0

        if(tmp_Byte == 0B111):
            k = 2088960.0

        return k

    def get_coefficients(self):
        self.get_c0()
        self.get_c00()
        self.get_c01()
        self.get_c1()
        self.get_c10()
        self.get_c11()
        self.get_c20()
        self.get_c21()
        self.get_c30()
    
    def get_c0(self):
        tmp_MSB = bus.read_byte_data(self.i2c_address, 0x10)
        tmp_LSB = bus.read_byte_data(self.i2c_address, 0x11)

        tmp_LSB = tmp_LSB >> 4;
        tmp = tmp_MSB << 4 | tmp_LSB

        if (tmp & (1 << 11)):
            tmp = tmp | 0xF000
        self.c0 = np.int16(tmp)
        return 

    def get_c1(self):
        tmp_MSB = bus.read_byte_data(self.i2c_address, 0x11)
        tmp_LSB = bus.read_byte_data(self.i2c_address, 0x12)

        tmp_LSB = bus.read_byte_data(self.i2c_address, 0xF)
        tmp = tmp_MSB << 8 | tmp_LSB

        if (tmp & (1 << 11)):
            tmp = tmp | 0xF000
        self.c1 = np.int16(tmp)
        return 

    def get_c00(self):
        tmp_MSB = bus.read_byte_data(self.i2c_address, 0x13)
        tmp_LSB = bus.read_byte_data(self.i2c_address, 0x14)
        tmp_XLSB = bus.read_byte_data(self.i2c_address, 0x15)

        tmp = np.uint32(tmp_MSB << 12) | np.uint32(tmp_LSB << 4) | np.uint32(tmp_XLSB >> 4)

        if(tmp & (1 << 19)):
            tmp = tmp | 0XFFF00000
        self.c00 = np.int32(tmp)
        return 

    def get_c10(self):
        tmp_MSB = bus.read_byte_data(self.i2c_address, 0x15)
        tmp_LSB = bus.read_byte_data(self.i2c_address, 0x16)
        tmp_XLSB = bus.read_byte_data(self.i2c_address, 0x17)

        tmp_MSB = tmp_MSB & 0xF

        #tmp = tmp_MSB << 8 | tmp_LSB
        #tmp = tmp << 8
        tmp = np.uint32(tmp_MSB << 16) | np.uint32(tmp_LSB << 8) | np.uint32(tmp_XLSB)

        if(tmp & (1 << 19)):
            tmp = tmp | 0XFFF00000
        self.c10 = np.int32(tmp)
        return 

    def get_c01(self):
        tmp_MSB = bus.read_byte_data(self.i2c_address, 0x18)
        tmp_LSB = bus.read_byte_data(self.i2c_address, 0x19)

        tmp = (tmp_MSB << 8) | tmp_LSB
        self.c01 = np.int16(tmp)
        return 

    def get_c11(self):
        tmp_MSB = bus.read_byte_data(self.i2c_address, 0x1A)
        tmp_LSB = bus.read_byte_data(self.i2c_address, 0x1B)

        tmp = (tmp_MSB << 8) | tmp_LSB
        self.c11 = np.int16(tmp)
        return 

    def get_c20(self):
        tmp_MSB = bus.read_byte_data(self.i2c_address, 0x1C)
        tmp_LSB = bus.read_byte_data(self.i2c_address, 0x1D)

        tmp = (tmp_MSB << 8) | tmp_LSB
        self.c20 = np.int16(tmp)
        return

    def get_c21(self):
        tmp_MSB = bus.read_byte_data(self.i2c_address, 0x1E)
        tmp_LSB = bus.read_byte_data(self.i2c_address, 0x1F)

        tmp = (tmp_MSB << 8) | tmp_LSB
        self.c21 = np.int16(tmp)
        return

    def get_c30(self):
        tmp_MSB = bus.read_byte_data(self.i2c_address, 0x20)
        tmp_LSB = bus.read_byte_data(self.i2c_address, 0x21)

        tmp = (tmp_MSB << 8) | tmp_LSB
        self.c30 = np.int16(tmp)
        return
    
    
    