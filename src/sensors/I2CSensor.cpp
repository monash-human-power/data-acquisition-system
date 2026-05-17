#include "I2CSensor.h"

I2CSensor::I2CSensor(uint8_t id, I2CBus& bus, uint8_t addr) : SensorBase(id), bus(bus), deviceAddress(addr) {
    // Setup code if needed
};

I2CSensor::~I2CSensor(){
    // TODO: Implement destructor if needed, depending on connection method
};

bool I2CSensor::init() {
    // TODO: Make this function, all I2C should init the same way
};
