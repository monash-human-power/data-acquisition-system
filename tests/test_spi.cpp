#include "hardware/SPIBus.h"

#include <iostream>
#include <vector>

int main()
{
    SPIBus spi("/dev/spidev0.0", 1000000, 0);

    if (!spi.openBus()) {
        std::cerr << "SPI initialisation failed\n";
        return 1;
    }

    std::vector<uint8_t> tx = {0xAA, 0x55};
    std::vector<uint8_t> rx;

    if (spi.transfer(tx, rx)) {
        std::cout << "SPI transfer completed\n";

        for (uint8_t byte : rx) {
            std::cout << static_cast<int>(byte) << " ";
        }

        std::cout << std::endl;
    } else {
        std::cerr << "SPI transfer failed\n";
        return 1;
    }

    return 0;
}
