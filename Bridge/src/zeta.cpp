#include "zeta.hpp"

#include <chrono>
#include <iostream>

ZetaRfRadio::ZetaRfRadio()
{
    std::cout << "Starting Zeta Radio..." << std::endl;

    if (!this->zeta_.beginWithPacketLengthOf(PACKET_LENGTH))
        throw "ZetaRf begin failed. Check wiring?";

    if (!this->zeta_.startListeningSinglePacketOnChannel(ZetaRfRadio::ZETA_CHANNEL))
        throw "ZetaRf startListening failed.";

    std::cout << "Init done." << std::endl;

    std::cout << "Starting worker..." << std::endl;
    this->worker_ = std::thread(&ZetaRfRadio::watch_send_queue, this);
}

ZetaRfRadio::~ZetaRfRadio()
{
    if (this->worker_.joinable())
    {
        std::cout << "Attempting to join worker..." << std::endl;
        this->should_worker_join_ = true;
        this->worker_.join();
        std::cout << "Joined!" << std::endl;
    }
}

void ZetaRfRadio::set_on_received(std::function<void(Frame)> callback)
{
    this->on_receive_ = callback;
}

void ZetaRfRadio::send_packets(const std::vector<Frame> frames)
{
    this->send_queue_.push(frames);
}

void ZetaRfRadio::watch_send_queue()
{
    while (!this->should_worker_join_)
    {
        std::cout << "Worker is working..." << std::endl;

        if (auto packet = this->send_queue_.pop())
            std::cout << "Would send packet: " << &*packet << std::endl;

        std::this_thread::sleep_for(std::chrono::seconds(1));
    }
    std::cout << "Worker thread exiting" << std::endl;
}
