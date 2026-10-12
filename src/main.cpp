#include "src/core/VCUController.h"
#include "src/sensors/Camera.h"

#include <iostream>
#include <csignal>
#include <cstdlib>

Camera* activeCamera = nullptr;

void handleSignal(int signal)
{
    if (signal == SIGINT)
    {
        std::cout << "\nStopping VCU..." << std::endl;

        if (activeCamera != nullptr)
        {
            std::cout << "Stopping camera stream..." << std::endl;
            activeCamera->stopStream();
        }

        std::cout << "VCU stopped." << std::endl;

        std::exit(0);
    }
}

int main()
{
    // Handle Ctrl+C
    std::signal(SIGINT, handleSignal);

    try
    {
        Camera camera;
        activeCamera = &camera;

        if (!camera.startStream())
        {
            std::cerr << "Warning: Camera stream failed to start."
                      << std::endl;
        }
        else
        {
            std::cout << "Camera stream started." << std::endl;
        }

        VCUController controller;

        std::cout << "VCU running. Press Ctrl+C to stop."
                  << std::endl;

        controller.run();

        // In case controller.run() exits normally
        camera.stopStream();
        activeCamera = nullptr;
    }
    catch (const std::exception& error)
    {
        if (activeCamera != nullptr)
        {
            activeCamera->stopStream();
        }

        std::cerr << "VCU failed to start: "
                  << error.what()
                  << std::endl;

        return 1;
    }

    return 0;
}