#include "HumiditySensor.h"
#include <iostream>
#include <chrono>
#include <thread>

HumiditySensor::HumiditySensor(I2CBus& sharedBus, int id, int addr)
    : I2CSensor(sharedBus, id, addr) {}

bool HumiditySensor::init() {
    // 0x94 is soft reset
    if (bus.writeCommand(deviceAddress, 0x94)) {
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
        std::cout << "SHT40 Humidity Sensor Initialized at 0x" << std::hex << (int)deviceAddress << std::dec << "\n";
        return true;
    }
    return false;
}

SensorReading HumiditySensor::read() {
    SensorReading reading;
    reading.sensorID = this->sensorID; 
    reading.isValid = false;

    // 0xFD is temp and relative humidity in high precision
    if (!bus.writeCommand(deviceAddress, 0xFD)) {
        std::cerr << "SHT40 (RH): Failed to send measure command.\n";
        return reading; 
    }

    std::this_thread::sleep_for(std::chrono::milliseconds(10));

    // Returns 6 bytes
    const std::vector<uint8_t> rx_bytes = bus.readBytes(deviceAddress, 6);
    
    if (rx_bytes.size() != 6) {
        std::cerr << "SHT40 (RH): Read failed or returned incomplete data.\n";
        return reading;
    }

    // Third and fourth bytes are humidity
    uint16_t rh_ticks = (rx_bytes[3] << 8) | rx_bytes[4];
    
    // From datasheet
    float rh = -6.0f + 125.0f * (static_cast<float>(rh_ticks) / 65535.0f);

    // Crops to 0-100% relative to cut out over/under measures (datasheet recommends)
    if (rh > 100.0f) {
        rh = 100.0f;
    } else if (rh < 0.0f) {
        rh = 0.0f;
    }

    reading.value = rh;
    reading.isValid = true;
    return reading;
}