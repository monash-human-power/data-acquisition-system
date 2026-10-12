#include "GPIOInput.h"

#include <fcntl.h>
#include <poll.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/gpio.h>

#include <cstdio>
#include <cstring>
#include <iostream>

GPIOInput::GPIOInput(
    const std::string& chipLabel,
    unsigned int line
)
    : chipLabel(chipLabel),
      line(line),
      fd(-1)
{
}

GPIOInput::~GPIOInput()
{
    closeLine();
}

bool GPIOInput::openLine()
{
    if (isOpen()) {
        return true;
    }

    // Find the chip with the matching label
    int chipFd = -1;

    for (int i = 0; i < 16 && chipFd < 0; ++i) {
        std::string path = "/dev/gpiochip" + std::to_string(i);

        int candidate = open(path.c_str(), O_RDWR | O_CLOEXEC);

        if (candidate < 0) {
            continue;
        }

        gpiochip_info info{};

        if (ioctl(candidate, GPIO_GET_CHIPINFO_IOCTL, &info) == 0 &&
            chipLabel == info.label &&
            line < info.lines) {
            chipFd = candidate;
        } else {
            close(candidate);
        }
    }

    if (chipFd < 0) {
        std::cerr << "GPIO chip '" << chipLabel
                  << "' not found (or no permission to open it)" << std::endl;
        return false;
    }

    gpio_v2_line_request request{};

    request.offsets[0] = line;
    request.num_lines = 1;
    request.config.flags =
        GPIO_V2_LINE_FLAG_INPUT | GPIO_V2_LINE_FLAG_EDGE_FALLING;

    std::strncpy(request.consumer, "vcu", sizeof(request.consumer) - 1);

    int result = ioctl(chipFd, GPIO_V2_GET_LINE_IOCTL, &request);

    close(chipFd);

    if (result < 0) {
        perror("GPIO line request failed");
        return false;
    }

    fd = request.fd;

    std::cout << "GPIO initialised: "
              << chipLabel
              << " line " << line << std::endl;

    return true;
}

void GPIOInput::closeLine()
{
    if (fd >= 0) {
        close(fd);
        fd = -1;
    }
}

bool GPIOInput::isOpen() const
{
    return fd >= 0;
}

void GPIOInput::discardEdges()
{
    if (!isOpen()) {
        return;
    }

    pollfd pfd{fd, POLLIN, 0};
    gpio_v2_line_event event{};

    while (poll(&pfd, 1, 0) > 0 && (pfd.revents & POLLIN)) {
        if (read(fd, &event, sizeof(event)) != sizeof(event)) {
            break;
        }
    }
}

int GPIOInput::waitForFallingEdge(int timeoutMs)
{
    if (!isOpen()) {
        return -1;
    }

    pollfd pfd{fd, POLLIN, 0};

    int ready = poll(&pfd, 1, timeoutMs);

    if (ready == 0) {
        return 0;
    }

    if (ready < 0 || !(pfd.revents & POLLIN)) {
        return -1;
    }

    gpio_v2_line_event event{};

    if (read(fd, &event, sizeof(event)) != sizeof(event)) {
        return -1;
    }

    return 1;
}
