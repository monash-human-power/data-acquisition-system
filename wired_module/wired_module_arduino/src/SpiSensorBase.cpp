#include "SpiSensorBase.h"
#include <cstring>
#include <cstdio>
#include "esp_err.h"

SpiSensorBase::SpiSensorBase(spi_device_handle_t spiHandle, uint8_t sensorID)
    : spiHandle(spiHandle) {
    this->sensorID = sensorID;  // Inherit from SensorBase: sensorID attribute.
}

// Read sensor register
void SpiSensorBase::read_sensor_register(uint8_t registerAddress, size_t readLength) {

  
    uint8_t tx[readLength + 1];
    uint8_t rx[readLength + 1];
    
    memset(tx, 0, sizeof(tx));
    memset(rx, 0, sizeof(rx));


    // Transaction
    tx[0] = registerAddress;  // | 0x80; // MSB 1 = read (for MPU)

    spi_transaction_t t = {};
    t.length = 8 * (readLength + 1);  
    t.tx_buffer = tx;
    t.rx_buffer = rx;

    ESP_ERROR_CHECK(spi_device_transmit(this->spiHandle, &t));

    // skip 1st byte
    memcpy(this->readBuffer, &rx[1], readLength);

};

void SpiSensorBase::write_sensor_register(uint8_t registerAddress, uint8_t data) {
    uint8_t tx[2] = { registerAddress , data };  // MPU -  add &0x7F - MSB = 0 → write

    spi_transaction_t t = {};
    t.flags = 0;
    t.length = 16;
    t.tx_buffer = tx;
    t.rx_buffer = nullptr;

    ESP_ERROR_CHECK(spi_device_transmit(this->spiHandle, &t));
}

int32_t SpiSensorBase::convert_two_complement(uint32_t data, uint8_t length) {
    if (data & (1 << (length - 1))) {
        data -= (1 << length);
    }
    return data;
}

void SpiSensorBase::print_read_buffer() {
    for (size_t i = 0; i < sizeof(this->readBuffer); i++) {
        printf("%d: 0x%02x\n", (int)i, this->readBuffer[i]);
    }
}
