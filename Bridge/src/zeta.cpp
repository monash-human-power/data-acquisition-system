#include "zeta.hpp"

#include <chrono>
#include <iostream>

#include "debug.hpp"

ZetaRfRadio::ZetaRfRadio()
{
    std::cout << "Starting Zeta Radio..." << std::endl;

    if (!this->zeta_.beginWithPacketLengthOf(PACKET_LENGTH))
        throw "ZetaRf begin failed. Check wiring?";

    if (!this->zeta_.startListeningSinglePacketOnChannel(ZetaRfRadio::ZETA_CHANNEL))
        throw "ZetaRf startListening failed.";

    debug << "Starting ZetaRf worker thread..." << std::endl;
    this->worker_ = std::thread(&ZetaRfRadio::rx_tx_loop, this);

    std::cout << "ZetaRf init done." << std::endl;
}

ZetaRfRadio::~ZetaRfRadio()
{
    if (this->worker_.joinable())
    {
        this->should_worker_join_ = true;
        this->worker_.join();
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

void ZetaRfRadio::rx_tx_loop()
{
    while (!this->should_worker_join_)
    {
        // Receive packet
        this->process_zeta_events();
        if (this->zeta_.hasDataAvailable())
            this->read_packet();

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

void ZetaRfRadio::process_zeta_events()
{
    const auto event = this->zeta_.checkForEvent();
    if (event & ZetaRf::Event::DeviceBusy)
    {
        // DeviceBusy error usually means the radio module is unresponsive and
        // needs a reset.
        std::cout << "Error: Device Busy! Restarting..." << std::endl;

        if (!this->zeta_.beginWithPacketLengthOf(PACKET_LENGTH))
            std::cout << "ZetaRf begin failed after comm error." << std::endl;
        this->zeta_.restartListeningSinglePacket();
    }
    if (event & ZetaRf::Event::PacketReceived)
    {
        // We'll read data later
        // Get RSSI (only valid in single packet RX, before going back to RX)
        // See https://www.silabs.com/documents/public/data-sheets/Si4455.pdf
        const auto rssi = (float) this->zeta_.latchedRssiValue() / 2 - 130;

        // Restart listening on the same channel
        this->zeta_.restartListeningSinglePacket();

        debug << "Packet received with RSSI: " << rssi << " dBm" << std::endl;
    }
}

void ZetaRfRadio::read_packet()
{
    uint8_t packet_bytes[PACKET_LENGTH];
    const auto read_result = this->zeta_.readPacketTo(packet_bytes);

    if (read_result)
    {
        auto packet = reinterpret_cast<const Frame *>(packet_bytes);
        debug << "Packet received: " << &*packet << std::endl;
        this->on_receive_(*packet);
    }
    else
    {
        std::cerr << "read_packet failed with code ["
                  << read_result.value() << "]" << std::endl;
    }
}

void ZetaRfRadio::transmit_packet(const Frame packet)
{
    const auto bytes = reinterpret_cast<const uint8_t *>(&packet);
    if (!this->zeta_.sendFixedLengthPacketOnChannel(ZETA_CHANNEL, bytes))
        std::cerr << "Packet failed to send" << std::endl;
}
