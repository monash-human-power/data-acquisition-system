#include "CurrentSensor.h"
#include <iostream>
#include <chrono>

CurrentSensor::CurrentSensor(std::string id, I2CBus& sharedBus, uint8_t addr)
    : I2CSensor(id, sharedBus, addr) {}

bool CurrentSensor::init() {
    // 0x36 is MAX17320 address, battery current is on register 0x1C
    std::vector<uint8_t> testRead = bus.readRegisters(0x36, 0x1C, 2);
    if (testRead.empty()) {
        return false;
    }
    return true;
}

bool CurrentSensor::read() {
    SensorReading reading;
    reading.isValid = false;

    // 2 byte current
    std::vector<uint8_t> currData = bus.readRegisters(0x36, 0x1C, 2);

    if (currData.empty()) {
        this->lastReading = reading;
        return false;
    }
    
    // Read as LSB first
    // int16_t as it can go negative if recharging not discharging
    int16_t rawCurrent = (currData[1] << 8) | currData[0];
    
    // From datasheet: Convert to Volts (1.5625 uV per LSB), then divide by sense resistor
    float currentAmps = (rawCurrent * 0.0000015625f) / SENSE_RESISTOR_OHMS;

    reading.value = currentAmps;
    
    reading.timestamp = std::chrono::duration_cast<std::chrono::milliseconds>(
                               std::chrono::system_clock::now().time_since_epoch()
                           ).count();
    reading.isValid = true;

    this->lastReading = reading;

    return true;
}