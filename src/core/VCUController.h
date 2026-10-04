#pragma once

#include "SystemConfig.h"
#include "SensorManager.h"
#include "CommunicationManager.h"
#include "I2CBus.h"

#include "../sensors/GyroscopeSensor.h"

#include <memory>

class VCUController
{
public:
    VCUController();

    void setup();
    void run();

private:
    SystemConfig config;

    std::unique_ptr<I2CBus> i2cBus;

    std::shared_ptr<GyroscopeSensor> gyroSensor;

    SensorManager sensorManager;
    CommunicationManager communicationManager;

    bool running;
};