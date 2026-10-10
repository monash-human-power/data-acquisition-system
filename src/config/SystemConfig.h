#pragma once

#include <string>

class SystemConfig
{
public:
    SystemConfig();

    std::string getI2CDevicePath() const;

    std::string getSPIDevicePath() const;

    unsigned int getSPISpeedHz() const;

    std::string getStrainDrdyChipLabel() const;

    unsigned int getStrainDrdyLine() const;

    int getSensorReadIntervalMs() const;

    std::string getDeviceName() const;

    bool isDebugEnabled() const;

private:
    std::string i2cDevicePath;
    std::string spiDevicePath;
    unsigned int spiSpeedHz;
    std::string strainDrdyChipLabel;
    unsigned int strainDrdyLine;
    int sensorReadIntervalMs;
    std::string deviceName;
    bool debugEnabled;
};