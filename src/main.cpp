#include "SensorManager.h"

#include <chrono>
#include <iostream>
#include <thread>

int main()
{
    SensorManager sensorManager;

    bool initSuccess = sensorManager.initAll();

    if (!initSuccess)
    {
        std::cerr << "Warning: one or more sensors failed to initialise." << std::endl;
    }

    while (true)
    {
        sensorManager.readAll();

        auto packets = sensorManager.serializeAll();

        for (const auto& packet : packets)
        {
            std::cout << packet << std::endl;
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }

    return 0;
}