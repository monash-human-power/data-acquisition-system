#include "radio.hpp"

#include <thread>

#include "debug.hpp"

Radio::~Radio()
{
    if (this->worker_.joinable())
    {
        this->should_worker_join_ = true;
        this->worker_.join();
    }
}

void Radio::set_on_received(std::function<void(Frame)> callback)
{
    this->on_receive_ = callback;
}

void Radio::send_packets(const std::vector<Frame> frames)
{
    this->send_queue_.push(frames);
}

void Radio::rx_tx_loop()
{
    while (!this->should_worker_join_)
    {
        // Check for radio events, receive packets, etc.
        this->loop_tick();

        // Transmit next queued packet.
        // We could send all queue packets, but we don't want to overwhelm the
        // receiver's rx fifo if it is also transmitting.
        if (auto packet = this->send_queue_.pop())
        {
            debug << "Sending packet: " << &*packet << std::endl;
            this->transmit_packet(*packet);
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(2));
    }
    debug << "ZetaRf worker thread exiting..." << std::endl;
}