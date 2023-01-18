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
     * @param is_bike True if the this is run on the bike, false for the chase car.
     * @param ce_pin The GPIO pin to use for the CE (chip enable) pin.
     * @param cs_pin The GPIO pin to use for the CS (chip select) pin.
     */
    Nrf24Radio(bool is_bike, uint16_t ce_pin, uint16_t cs_pin);
};

/** Smart/shared pointer to an Nrf24Radio */
using Nrf24Radio_ptr = Nrf24Radio::ptr_t;