#include "VCUController.h"

#include <chrono>
#include <iostream>
#include <memory>
#include <thread>

VCUController::VCUController()
    : config(),
      i2cBus(nullptr),
      gyroSensor(nullptr),
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
        std::cerr
            << "Warning: communication failed to initialise."
            << std::endl;
    }

    try
    {
        // Temporary direct MPU6050 connection on Raspberry Pi I2C bus 1.
        i2cBus = std::make_unique<I2CBus>("/dev/i2c-1");

        gyroSensor = std::make_shared<GyroscopeSensor>(
            "gyro_1",
            *i2cBus
        );

        sensorManager.addSensor(gyroSensor);
    }
    catch (const std::exception& e)
    {
        std::cerr
            << "Failed to set up gyroscope: "
            << e.what()
            << std::endl;
    }

    bool initSuccess = sensorManager.initAll();

    if (!initSuccess)
    {
        std::cerr
            << "Warning: one or more sensors failed to initialise."
            << std::endl;
    }

    if (initSuccess && gyroSensor)
    {
        std::cout
            << "Keep gyroscope still for calibration..."
            << std::endl;

        gyroSensor->calibrateGyroscope();

        std::cout
            << "Gyroscope calibration complete."
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

        std::vector<std::string> packets =
            sensorManager.serializeAll();

        communicationManager.sendMessages(packets);

        std::this_thread::sleep_for(
            std::chrono::milliseconds(
                config.getSensorReadIntervalMs()
            )
        );
    }
}