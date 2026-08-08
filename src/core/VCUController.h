#pragma once

#include "SystemConfig.h"
#include "SensorManager.h"
#include "I2CBus.h"

class VCUController
{
public:
    VCUController();

    void setup();

    void run();

private:
    SystemConfig config;
    I2CBus i2cBus;
    SensorManager sensorManager;

    bool running;
};