#include "SystemConfig.h"

SystemConfig::SystemConfig()
    : i2cDevicePath("/dev/i2c-1"),
      spiDevicePath("/dev/spidev0.0"),
      spiSpeedHz(1000000),
      // ADS131M08 DRDY: HAT J8 ISO-INT0 -> header pin 18 (GPIO 24)
      strainDrdyChipLabel("pinctrl-rp1"),
      strainDrdyLine(24),
      sensorReadIntervalMs(100),
      deviceName("MHP-VCU"),
      debugEnabled(true)
{
}

std::string SystemConfig::getI2CDevicePath() const
{
    return i2cDevicePath;
}

std::string SystemConfig::getSPIDevicePath() const
{
    return spiDevicePath;
}

unsigned int SystemConfig::getSPISpeedHz() const
{
    return spiSpeedHz;
}

std::string SystemConfig::getStrainDrdyChipLabel() const
{
    return strainDrdyChipLabel;
}

unsigned int SystemConfig::getStrainDrdyLine() const
{
    return strainDrdyLine;
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