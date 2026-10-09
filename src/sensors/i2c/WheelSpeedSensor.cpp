#include "WheelSpeedSensor.h"
#include <iostream>
#include <chrono>
#include <cstring> // Required for std::memcpy

WheelSpeedSensor::WheelSpeedSensor(std::string id, I2CBus& sharedBus, uint8_t addr)
    : I2CSensor(id, sharedBus, addr) {}

bool WheelSpeedSensor::init() {
    // Verify that it is active
    std::vector<uint8_t> testRead = bus.readBytes(deviceAddress, 4);
    
    if (testRead.empty() || testRead.size() != 4) {
        return false;
    }
    return true;
}

bool WheelSpeedSensor::read() {
    // Formatting may change once the ATTiny code is finalised and flashed
    SensorReading reading;
    reading.isValid = false;

    // Request 4 bytes (the IEEE 754 float) from the ATTiny
    std::vector<uint8_t> speedData = bus.readBytes(deviceAddress, 4);

    if (speedData.empty() || speedData.size() != 4) {
        this->lastReading = reading;
        return false;
    }
    
    // Little-endian from ATTiny
    uint32_t rawBits = (speedData[3] << 24) | 
                       (speedData[2] << 16) | 
                       (speedData[1] << 8)  | 
                       speedData[0];
    
    // Safely copy the raw 32-bit integer bits into a float memory space.
    // This avoids "strict aliasing" rule violations in C++.
    float speed = 0.0f;
    std::memcpy(&speed, &rawBits, sizeof(float));

    reading.value = speed;
    
    reading.timestamp = std::chrono::duration_cast<std::chrono::milliseconds>(
                            std::chrono::system_clock::now().time_since_epoch()
                        ).count();
    reading.isValid = true;

    this->lastReading = reading;

    return true;
}