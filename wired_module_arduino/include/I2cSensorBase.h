#ifndef I2C_SENSOR_BASE_H
#define I2C_SENSOR_BASE_H

#include "SensorBase.h"
#include "driver/i2c.h"

class I2cSensorBase : public SensorBase {
public:
    // Attributes
    uint8_t sensorAddress;
    i2c_port_t masterPortNum;
    uint8_t readBuffer[8];

    // Constructor
    explicit I2cSensorBase(i2c_port_t masterPortNum, uint8_t sensorAddress, uint8_t sensorID);

    // Methods
    void configure() override = 0;       // Declare configure method
    void read() override = 0;            // Declare read method
    String generateJson() override;      // Declare generateJson method
    void send() override;                // Declare send method

    void read_sensor_register(uint8_t registerAddress, size_t readLength, int timeout);
    void write_sensor_register(uint8_t registerAddress, uint8_t data, int timeout);

    int32_t convert_two_complement(uint32_t data, uint8_t length);
    void print_read_buffer();
};

#endif // I2C_SENSOR_BASE_H
