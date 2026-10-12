#pragma once

#include <string>

// A GPIO input that reports falling edges, using the Linux GPIO
// character device (/dev/gpiochipN, uAPI v2).
//
// The chip is found by its label rather than its /dev path because the
// numbering changes between kernels. On the Raspberry Pi 5 the 40-pin
// header GPIOs belong to the RP1 chip, labelled "pinctrl-rp1".
class GPIOInput {
private:
    std::string chipLabel;
    unsigned int line;
    int fd;

public:
    GPIOInput(
        const std::string& chipLabel = "pinctrl-rp1",
        unsigned int line = 24
    );

    // Virtual so tests can substitute a simulated pin.
    virtual ~GPIOInput();

    GPIOInput(const GPIOInput&) = delete;
    GPIOInput& operator=(const GPIOInput&) = delete;

    virtual bool openLine();
    void closeLine();

    virtual bool isOpen() const;

    // Drops edges that happened before this call.
    virtual void discardEdges();

    // Waits for the next falling edge.
    // Returns 1 on an edge, 0 on timeout and -1 on error.
    virtual int waitForFallingEdge(int timeoutMs);
};
