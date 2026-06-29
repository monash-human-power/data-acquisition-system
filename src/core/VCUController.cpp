#include "VCUController.h"

#include <chrono>
#include <iostream>
#include <thread>

VCUController::VCUController()
    : config(),
      i2cBus(config.getI2CDevicePath()),
      sensorManager(),
      running(false)
{
}

void VCUController::setup()
{
    std::cout << "Starting VCU system..." << std::endl;

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

        for (const std::string& packet : packets)
        {
            std::cout << packet << std::endl;
        }

        std::this_thread::sleep_for(
            std::chrono::milliseconds(config.getSensorReadIntervalMs())
        );
    }
}