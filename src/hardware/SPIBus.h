#pragma once

#include <cstdint>
#include <string>
#include <vector>

class SPIBus {
private:
    std::string devicePath;
    int fd;

    uint8_t mode;
    uint8_t bitsPerWord;
    uint32_t speedHz;

public:
    SPIBus(
        const std::string& device = "/dev/spidev0.0",
        uint32_t speed = 1000000,
        uint8_t spiMode = 0
    );

    ~SPIBus();

    SPIBus(const SPIBus&) = delete;
    SPIBus& operator=(const SPIBus&) = delete;

    bool openBus();
    void closeBus();

    bool transfer(
        const std::vector<uint8_t>& tx,
        std::vector<uint8_t>& rx
    );

    bool write(const std::vector<uint8_t>& data);

    bool isOpen() const;
};