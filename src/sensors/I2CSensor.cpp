#include "I2CSensor.h"

I2CSensor::I2CSensor(std::string id, I2CBus& bus, uint8_t addr) : SensorBase(id), bus(bus), deviceAddress(addr) {
    // Setup code if needed
};

I2CSensor::~I2CSensor(){
    // TODO: Implement destructor if needed, depending on connection method
};