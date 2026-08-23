#include "src/core/VCUController.h"

#include <iostream>

int main()
{
    try
    {
        VCUController controller;
        controller.run();
    }
    catch (const std::exception& error)
    {
        std::cerr << "VCU failed to start: "
                  << error.what()
                  << std::endl;

        return 1;
    }

    return 0;
}