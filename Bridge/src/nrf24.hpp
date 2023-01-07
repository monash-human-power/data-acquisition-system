#pragma once

#include <memory>

#include <RF24/RF24.h>

#include "radio.hpp"

class Nrf24Radio : public Radio
{
private:
    RF24 nrf24_;

    void loop_tick();
    void transmit_packet(const Frame packet);

public:
    /** Smart/shared pointer to this class. */
    using ptr_t = std::shared_ptr<Nrf24Radio>;

    /**
     * Create a Radio which can be used to transmit and receive radio messages.
     */
    Nrf24Radio();
};

/** Smart/shared pointer to an Nrf24Radio */
using Nrf24Radio_ptr = Nrf24Radio::ptr_t;