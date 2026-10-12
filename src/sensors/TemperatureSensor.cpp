#include "TemperatureSensor.h"

#include <chrono>
#include <cstdint>
#include <iostream>
#include <thread>

TemperatureSensor::TemperatureSensor(
    const std::string& id,
    I2CBus& bus)
    : I2CSensor(id, bus, ADDRESS)
{
    lastReading.sensorID = sensorID;
    lastReading.timestamp = 0;
    lastReading.value = 0.0f;
    lastReading.isValid = false;
}

bool TemperatureSensor::init()
{
    auto whoami =
        bus.readRegisters(
            deviceAddress,
            WHOAMI_REG,
            1
        );

    if (whoami.size() != 1)
    {
        std::cerr
            << sensorID
            << ": could not read WHOAMI"
            << std::endl;

        return false;
    }

    if (whoami[0] != WHOAMI_VALUE)
    {
        std::cerr
            << sensorID
            << ": WHOAMI = 0x"
            << std::hex
            << static_cast<int>(whoami[0])
            << ", expected 0x"
            << static_cast<int>(WHOAMI_VALUE)
            << std::dec
            << std::endl;

        return false;
    }

    // Power down before changing configuration.
    if (!bus.writeRegister(
            deviceAddress,
            CTRL_REG,
            0x00))
    {
        return false;
    }

    // Configure STTS22H for free-running 25 Hz operation.
    if (!bus.writeRegister(
            deviceAddress,
            CTRL_REG,
            0x4C))
    {
        return false;
    }

    // Allow first temperature conversion to complete.
    std::this_thread::sleep_for(
        std::chrono::milliseconds(60)
    );

    std::cout
        << sensorID
        << ": temperature sensor initialised successfully"
        << std::endl;

    return true;
}

bool TemperatureSensor::read()
{
    auto data =
        bus.readRegisters(
            deviceAddress,
            TEMP_LOW_REG,
            2
        );

    lastReading.sensorID = sensorID;
    lastReading.timestamp = currentTimestampMs();

    if (data.size() != 2)
    {
        lastReading.isValid = false;
        return false;
    }

    uint16_t rawUnsigned =
        static_cast<uint16_t>(
            (static_cast<uint16_t>(data[1]) << 8) |
            data[0]
        );

    int16_t rawTemperature =
        static_cast<int16_t>(rawUnsigned);

    float temperatureC =
        static_cast<float>(rawTemperature) / 100.0f;

    lastReading.value = temperatureC;
    lastReading.isValid = true;

    return true;
}

std::uint64_t TemperatureSensor::currentTimestampMs()
{
    return static_cast<std::uint64_t>(
        std::chrono::duration_cast<
            std::chrono::milliseconds
        >(
            std::chrono::system_clock::now()
                .time_since_epoch()
        ).count()
    );
}