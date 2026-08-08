#pragma once

#include <string>

class SystemConfig
{
public:
    SystemConfig();

    std::string getI2CDevicePath() const;

    int getSensorReadIntervalMs() const;

    std::string getDeviceName() const;

    bool isDebugEnabled() const;

private:
    std::string i2cDevicePath;
    int sensorReadIntervalMs;
    std::string deviceName;
    bool debugEnabled;
};