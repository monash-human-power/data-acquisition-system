#include "I2cSensorBase.h"

I2cSensorBase::I2cSensorBase(i2c_port_t masterPortNum, uint8_t sensorAddress, uint8_t sensorID) {
    this->masterPortNum = masterPortNum;
    this->sensorAddress = sensorAddress;
    this->sensorID = sensorID;
}

void I2cSensorBase::read_sensor_register(uint8_t registerAddress, size_t readLength, int timeout) {
    ESP_ERROR_CHECK(i2c_master_write_read_device(this->masterPortNum, this->sensorAddress, &registerAddress,
                                 1, this->readBuffer, readLength, timeout));
}

void I2cSensorBase::write_sensor_register(uint8_t registerAddress, uint8_t data, int timeout) {
    uint8_t writeBuf[2];  // writeBuf[len+1];
    writeBuf[0] = registerAddress;
    writeBuf[1] = data;
    ESP_ERROR_CHECK(i2c_master_write_to_device(this->masterPortNum, this->sensorAddress, writeBuf, 2, timeout));
}

void I2cSensorBase::print_read_buffer() {
    for (int i = 0; i < sizeof(this->readBuffer); i++) {
        printf("%d:0x%02x\n",i,this->readBuffer[i]);
    }
}

int32_t I2cSensorBase::convert_two_complement(uint32_t data, uint8_t length){
    if (data & 1 << (length - 1)){
        data -= 2^length;
    }
    return data; 
}