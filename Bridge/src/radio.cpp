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
    // Check if there is too much in the queue and drop the oldest packets if needed.
    const int max_queue_size = 200;
    int cur_queue_size = this->send_queue_.size();
    if (cur_queue_size > max_queue_size) {
        // Queue is too long. Drop the oldest packets.
        // NOTE: This may cause an issue in high congestion situations where all
        // messages have at least one packet lost and are subsequently dropped.
        printf("Dropping one or more packets as queue too long.\n");
        for (int i = cur_queue_size; i > max_queue_size; i--)
        {
            this->send_queue_.pop();
        }
    }
    printf("%d packets in queue\n", this->send_queue_.size());
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