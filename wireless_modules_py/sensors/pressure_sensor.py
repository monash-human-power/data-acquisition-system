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
        Initialise the Barometer to read air pressure
        :param port: The i2c address that the barometer is connected to.
        """
        self.i2c_address = port
        i2c_ch = 1
        self.readings = []

        self.query_time = 0
        self.MS_TO_SEC = 1/1000
        self.NS_TO_MS = 1000000


    def read(self):
        raise NotImplemented

        # update the last time of read() being called
        self.query_time = time.time_ns() * self.NS_TO_MS

        return self.readings
    
    
    def get_c0(self):
        tmp_MSB = bus.read_byte_data(self.i2c_address, 0x10)
        tmp_LSB = bus.read_byte_data(self.i2c_address, 0x11)

        tmp_LSB = tmp_LSB >> 4;
        tmp = tmp_MSB << 4 | tmp_LSB

        if (tmp & (1 << 11)):
            tmp = tmp | 0xF000

        return np.int16(tmp)

    def get_c1(self):
        tmp_MSB = bus.read_byte_data(self.i2c_address, 0x11)
        tmp_LSB = bus.read_byte_data(self.i2c_address, 0x12)

        tmp_LSB = bus.read_byte_data(self.i2c_address, 0xF)
        tmp = tmp_MSB << 8 | tmp_LSB

        if (tmp & (1 << 11)):
            tmp = tmp | 0xF000

        return np.int16(tmp)

    def get_c00(self):
        tmp_MSB = bus.read_byte_data(self.i2c_address, 0x13)
        tmp_LSB = bus.read_byte_data(self.i2c_address, 0x14)
        tmp_XLSB = bus.read_byte_data(self.i2c_address, 0x15)

        tmp = np.uint32(tmp_MSB << 12) | np.uint32(tmp_LSB << 4) | np.uint32(tmp_XLSB >> 4)

        if(tmp & (1 << 19)):
            tmp = tmp | 0XFFF00000
    
        return np.int32(tmp)

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

        return np.int32(tmp)

    def get_c01(self):
        tmp_MSB = bus.read_byte_data(self.i2c_address, 0x18)
        tmp_LSB = bus.read_byte_data(self.i2c_address, 0x19)

        tmp = (tmp_MSB << 8) | tmp_LSB

        return np.int16(tmp)

    def get_c11(self):
        tmp_MSB = bus.read_byte_data(self.i2c_address, 0x1A)
        tmp_LSB = bus.read_byte_data(self.i2c_address, 0x1B)

        tmp = (tmp_MSB << 8) | tmp_LSB

        return np.int16(tmp)

    def get_c20(self):
        tmp_MSB = bus.read_byte_data(self.i2c_address, 0x1C)
        tmp_LSB = bus.read_byte_data(self.i2c_address, 0x1D)

        tmp = (tmp_MSB << 8) | tmp_LSB

        return np.int16(tmp)

    def get_c21(self):
        tmp_MSB = bus.read_byte_data(self.i2c_address, 0x1E)
        tmp_LSB = bus.read_byte_data(self.i2c_address, 0x1F)

        tmp = (tmp_MSB << 8) | tmp_LSB

        return np.int16(tmp)

    def get_c30(self):
        tmp_MSB = bus.read_byte_data(self.i2c_address, 0x20)
        tmp_LSB = bus.read_byte_data(self.i2c_address, 0x21)

        tmp = (tmp_MSB << 8) | tmp_LSB

        return np.int16(tmp)
    
    
    