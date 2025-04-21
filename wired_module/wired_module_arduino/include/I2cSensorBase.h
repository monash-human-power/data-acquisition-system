#include "SensorBase.h"
#include "driver/i2c.h"

#ifndef I2C_BASE
#define I2C_BASE

class I2cSensorBase : public SensorBase {
   public:
    // Attributes
    uint8_t sensorAddress;
    i2c_port_t masterPortNum;
    uint8_t readBuffer[8];

    // Constructor
    explicit I2cSensorBase(i2c_port_t masterPortNum, uint8_t sensorAddress, uint8_t sensorID);

    // Methods
    void read_sensor_register(uint8_t registerAddress, size_t readLength, int timeout);
    void write_sensor_register(uint8_t registerAddress, uint8_t data, int timeout);
    
    int32_t convert_two_complement(uint32_t data, uint8_t length);
    void print_read_buffer();
};

#endif