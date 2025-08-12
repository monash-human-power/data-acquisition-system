#ifndef SPI_SENSOR_BASE_H
#define SPI_SENSOR_BASE_H

#include "SensorBase.h"
#include "driver/spi_master.h"

class SpiSensorBase : public SensorBase {
public:

    // Attributes
    spi_device_handle_t spiHandle;
    uint8_t readBuffer[8];  // kept same as i2c

    // Constructor

    SpiSensorBase(spi_device_handle_t spiHandle, uint8_t sensorID);

    // Methods

    void configure() override = 0;   // To be implemented by derived class
    void read() override = 0;        // To be implemented by derived class
    String generateJson() override = 0; // To be implemented by derived class

    // SPI-specific methods
    void read_sensor_register(uint8_t registerAddress, size_t readLength);
    void write_sensor_register(uint8_t registerAddress, uint8_t data);

    int32_t convert_two_complement(uint32_t data, uint8_t length);
    void print_read_buffer();
};

#endif  
