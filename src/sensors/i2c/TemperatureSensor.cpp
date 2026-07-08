#include "TemperatureSensor.h"
#include <sstream>
#include <iostream>
#include <chrono>
#include <thread>

TemperatureSensor::TemperatureSensor(std::string id, I2CBus& sharedBus, uint8_t addr)
    : I2CSensor(id, sharedBus, addr) {}

bool TemperatureSensor::init() {
    // 0x94 is soft reset command
    if (bus.writeCommand(deviceAddress, 0x94)) {
        std::this_thread::sleep_for(std::chrono::milliseconds(1)); // Wait 1ms for reset
        std::cout << "SHT40 Initialized at 0x" << std::hex << (int)deviceAddress << std::dec << "\n";
        return true;
    }
    return false;
}

bool TemperatureSensor::read() {
    SensorReading reading;
    reading.sensorID = this->sensorID; 
    reading.isValid = false;

    // 0xFD is read relative humidity and temp with high precision
    if (!bus.writeCommand(deviceAddress, 0xFD)) {
        std::cerr << "SHT40: Failed to send measure command.\n";
        this->lastReading = reading;
        return false; 
    }

    std::this_thread::sleep_for(std::chrono::milliseconds(10));

    // Returns 6 bytes (first two have the reading for temp)
    const std::vector<uint8_t> rx_bytes = bus.readBytes(deviceAddress, 6);
    
    if (rx_bytes.size() != 6) {
        std::cerr << "SHT40: Read failed or returned incomplete data.\n";
        this->lastReading = reading;
        return false;
    } 

    uint16_t t_ticks = (rx_bytes[0] << 8) | rx_bytes[1];
    
    // From datasheet
    float t_degC = -45.0f + 175.0f * (static_cast<float>(t_ticks) / 65535.0f);

    auto now = std::chrono::system_clock::now();
    uint64_t ms = std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()).count();

    reading.timestamp = ms;
    reading.isValid = true;

    this->lastReading = reading;
    return true;
}

std::string TemperatureSensor::serialize() const{
    std::stringstream ss;
    ss << this->lastReading.sensorID << "," << this->lastReading.timestamp << "," << this->lastReading.value << "," << this->lastReading.isValid;

    return ss.str();
}