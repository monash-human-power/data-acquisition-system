#include "VCUController.h"

#include "../sensors/test/DummySensor.h"

#include <chrono>
#include <iostream>
#include <memory>
#include <thread>

VCUController::VCUController()
    : config(),
      i2cBus(nullptr),
      sensorManager(),
      communicationManager(),
      running(false)
{
}

void VCUController::setup()
{
    std::cout << "Starting VCU system..." << std::endl;

    bool communicationReady = communicationManager.init();

    if (!communicationReady)
    {
        std::cerr << "Warning: communication failed to initialise."
                  << std::endl;
    }

    // Laptop/WSL test mode: use dummy sensor only.
    sensorManager.addSensor(std::make_shared<DummySensor>("dummy_sensor_1"));

    /*
    Raspberry Pi real hardware mode later:

    i2cBus = std::make_unique<I2CBus>(config.getI2CDevicePath());

    sensorManager.addSensor(
        std::make_shared<TemperatureSensor>("temperature_1", *i2cBus)
    );
    */

    bool initSuccess = sensorManager.initAll();

    if (!initSuccess)
    {
        std::cerr << "Warning: one or more sensors failed to initialise."
                  << std::endl;
    }

    running = true;

    std::cout << "VCU setup complete." << std::endl;
}

void VCUController::run()
{
    setup();

    while (running)
    {
        sensorManager.readAll();

        std::vector<std::string> packets = sensorManager.serializeAll();

        communicationManager.sendMessages(packets);

        std::this_thread::sleep_for(
            std::chrono::milliseconds(config.getSensorReadIntervalMs())
        );
    }
}