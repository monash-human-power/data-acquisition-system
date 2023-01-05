#pragma once

#include <functional>
#include <vector>

#include "frame.hpp"

class Radio
{
public:
    /** Smart/shared pointer to this class. */
    using ptr_t = std::shared_ptr<Radio>;

    /**
     * Create a Radio which can be used to transmit and receive radio messages.
     */
    Radio(){};
    /** Stop all background processors for the Radio */
    virtual ~Radio(){};

    /**
     * Set the function to be called when a radio packet is received.
     * @param callback The function which accepts a Frame to be called.
     */
    virtual void set_on_received(std::function<void(Frame)> callback) = 0;
    /**
     * Add a collection of packets/frames to the transmit queue.
     * @param frames The packets to be sent, in the order that they should be
     *               transmitted.
     */
    virtual void send_packets(const std::vector<Frame> frames) = 0;
};

/** Smart/shared pointer to a Radio */
using Radio_ptr = Radio::ptr_t;