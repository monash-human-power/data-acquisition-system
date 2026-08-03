#include "VoltageSensor.h"
#include <iostream>
#include <chrono>

VoltageSensor::VoltageSensor(std::string id, I2CBus& sharedBus, uint8_t addr)
    : I2CSensor(id, sharedBus, addr) {}

bool VoltageSensor::init() {
    // 0x36 is MAX17320 address, battery voltage is on register 0xDA
    std::vector<uint8_t> testRead = bus.readRegisters(0x36, 0xDA, 2);
    if (testRead.empty()) {
        return false;
    }
    return true;
}

bool VoltageSensor::read() {
    SensorReading reading;
    reading.isValid = false;

    // 2 byte voltage
    std::vector<uint8_t> voltData = bus.readRegisters(0x36, 0xDA, 2);

    if (voltData.empty()) {
        this->lastReading = reading;
        return false;
    }
    
    // Read as LSB first
    uint16_t rawVoltage = (voltData[1] << 8) | voltData[0];
    
    // From datasheet
    float voltage = rawVoltage * 0.0003125f;

    reading.value = voltage;
    
    reading.timestamp = std::chrono::duration_cast<std::chrono::milliseconds>(
                               std::chrono::system_clock::now().time_since_epoch()
                           ).count();
    reading.isValid = true;

    this->lastReading = reading;

    return true;
}