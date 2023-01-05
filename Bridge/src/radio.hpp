#pragma once

#include <functional>
#include <memory>
#include <thread>
#include <vector>

#include "frame.hpp"
#include "thread_queue.hpp"

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
    ~Radio();

    /**
     * Set the function to be called when a radio packet is received.
     * @param callback The function which accepts a Frame to be called.
     */
    void set_on_received(std::function<void(Frame)> callback);
    /**
     * Add a collection of packets/frames to the transmit queue.
     * @param frames The packets to be sent, in the order that they should be
     *               transmitted.
     */
    void send_packets(const std::vector<Frame> frames);

protected:
    /**
     * Start a loop which repeatedly checks for received packets (which are
     * then processed) and check for queued packets to be sent (which are will
     * then sent). The loop will run until `this->should_worker_join` is true.
     */
    void rx_tx_loop();
    /** Background thread which receives/transmits packets after initialisation. */
    std::thread worker_;

    /** Callback which is called when a packet is successfully received. */
    std::function<void(Frame)> on_receive_;

    /**
     * Called in the rx_tx_loop. Performs any periodically required actions
     * (e.g. receiving packets).
     */
    virtual void loop_tick() = 0;
    /**
     * Transmit a packet using the Zeta radio module.
     * @param packet The Frame to be sent.
     */
    virtual void transmit_packet(const Frame packet) = 0;

private:
    /** Queue of packets which have not yet been transmitted. */
    ThreadQueue<Frame> send_queue_;
    /** Specifies if the worker thread should stop. */
    bool should_worker_join_ = false;

    // Class is non-copyable
    Radio(const Radio &that) = delete;
    Radio &operator=(const Radio &that) = delete;
};

/** Smart/shared pointer to a Radio */
using Radio_ptr = Radio::ptr_t;