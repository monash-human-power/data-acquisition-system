#include "SPIBus.h"

#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/spi/spidev.h>

#include <iostream>

SPIBus::SPIBus(
    const std::string& device,
    uint32_t speed,
    uint8_t spiMode
)
    : devicePath(device),
      fd(-1),
      mode(spiMode),
      bitsPerWord(8),
      speedHz(speed)
{
}

SPIBus::~SPIBus()
{
    closeBus();
}

bool SPIBus::openBus()
{
    if (isOpen()) {
        return true;
    }

    fd = open(devicePath.c_str(), O_RDWR);

    if (fd < 0) {
        perror("SPI open failed");
        return false;
    }

    if (ioctl(fd, SPI_IOC_WR_MODE, &mode) < 0 ||
        ioctl(fd, SPI_IOC_WR_BITS_PER_WORD, &bitsPerWord) < 0 ||
        ioctl(fd, SPI_IOC_WR_MAX_SPEED_HZ, &speedHz) < 0) {

        perror("SPI configuration failed");
        closeBus();
        return false;
    }

    std::cout << "SPI initialised: "
              << devicePath
              << " at " << speedHz
              << " Hz" << std::endl;

    return true;
}

void SPIBus::closeBus()
{
    if (fd >= 0) {
        close(fd);
        fd = -1;
    }
}

bool SPIBus::transfer(
    const std::vector<uint8_t>& tx,
    std::vector<uint8_t>& rx
)
{
    if (!isOpen() || tx.empty()) {
        return false;
    }

    rx.resize(tx.size());

    spi_ioc_transfer transferConfig{};

    transferConfig.tx_buf =
        reinterpret_cast<uintptr_t>(tx.data());

    transferConfig.rx_buf =
        reinterpret_cast<uintptr_t>(rx.data());

    transferConfig.len = static_cast<uint32_t>(tx.size());

    transferConfig.speed_hz = speedHz;
    transferConfig.bits_per_word = bitsPerWord;

    int result = ioctl(
        fd,
        SPI_IOC_MESSAGE(1),
        &transferConfig
    );

    if (result < 0) {
        perror("SPI transfer failed");
        return false;
    }

    return true;
}

bool SPIBus::write(const std::vector<uint8_t>& data)
{
    std::vector<uint8_t> ignoredResponse;
    return transfer(data, ignoredResponse);
}

bool SPIBus::isOpen() const
{
    return fd >= 0;
}