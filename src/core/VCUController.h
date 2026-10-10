#pragma once

#include "SystemConfig.h"
#include "SensorManager.h"
#include "CommunicationManager.h"
#include "I2CBus.h"
#include "SPIBus.h"
#include "GPIOInput.h"

#include "../data/DataSerialiser.h"
#include "../sensors/GyroscopeSensor.h"
#include "../sensors/analog/StrainGaugeSensor.h"

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
    std::unique_ptr<SPIBus> spiBus;
    std::unique_ptr<GPIOInput> strainDrdy;

    std::shared_ptr<GyroscopeSensor> gyroSensor;
    std::shared_ptr<StrainGaugeSensor> strainSensor;

    SensorManager sensorManager;
    DataSerialiser dataSerialiser;
    CommunicationManager communicationManager;

    bool running;
};