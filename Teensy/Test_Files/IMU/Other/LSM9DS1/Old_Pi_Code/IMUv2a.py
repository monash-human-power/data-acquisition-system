import smbus
bus = smbus.SMBus(1)
from LSM9DS1 import *
import time


def detectIMU():
    try:
        LSM9DS1v2a_WHO_XG_response = (bus.read_byte_data(
            LSM9DS1v2a_GYR_ADDRESS, LSM9DS1_WHO_AM_I_XG))
        LSM9DS1v2a_WHO_M_response = (bus.read_byte_data(LSM9DS1v2a_MAG_ADDRESS, LSM9DS1_WHO_AM_I_M))

    except IOError as f:
        print ''  # need to do something here, so we just print a space
    else:
        if (LSM9DS1v2a_WHO_XG_response == 0x68) and (LSM9DS1v2a_WHO_M_response == 0x3d):
            print("\nFound LSM9DS1v2a\n")

    time.sleep(1)


def writeACC(register, value):
    bus.write_byte_data(LSM9DS1v2a_ACC_ADDRESS, register, value)
    return -1


def readACCx():
    acc_l = bus.read_byte_data(LSM9DS1v2a_ACC_ADDRESS, LSM9DS1_OUT_X_L_XL)
    acc_h = bus.read_byte_data(LSM9DS1v2a_ACC_ADDRESS, LSM9DS1_OUT_X_H_XL)

    acc_combined = (acc_l | acc_h << 8)
    return acc_combined if acc_combined < 32768 else acc_combined - 65536


def readACCy():
    acc_l = bus.read_byte_data(LSM9DS1v2a_ACC_ADDRESS, LSM9DS1_OUT_Y_L_XL)
    acc_h = bus.read_byte_data(LSM9DS1v2a_ACC_ADDRESS, LSM9DS1_OUT_Y_H_XL)

    acc_combined = (acc_l | acc_h << 8)
    return acc_combined if acc_combined < 32768 else acc_combined - 65536


def readACCz():
    acc_l = bus.read_byte_data(LSM9DS1v2a_ACC_ADDRESS, LSM9DS1_OUT_Z_L_XL)
    acc_h = bus.read_byte_data(LSM9DS1v2a_ACC_ADDRESS, LSM9DS1_OUT_Z_H_XL)

    acc_combined = (acc_l | acc_h << 8)
    return acc_combined if acc_combined < 32768 else acc_combined - 65536


def initIMU():
    # initialise the accelerometer
    writeACC(LSM9DS1_CTRL_REG5_XL, 0b00111000)  # z, y, x axis enabled for accelerometer
    writeACC(LSM9DS1_CTRL_REG6_XL, 0b11001000)  # 952 Hz, +/- 16g
