#include "SystemConfig.h"

SystemConfig::SystemConfig()
    : i2cDevicePath("/dev/i2c-1"),
      sensorReadIntervalMs(100),
      deviceName("MHP-VCU"),
      debugEnabled(true)
{
}

std::string SystemConfig::getI2CDevicePath() const
{
    return i2cDevicePath;
}

int SystemConfig::getSensorReadIntervalMs() const
{
    return sensorReadIntervalMs;
}

std::string SystemConfig::getDeviceName() const
{
    return deviceName;
}

bool SystemConfig::isDebugEnabled() const
{
    return debugEnabled;
}