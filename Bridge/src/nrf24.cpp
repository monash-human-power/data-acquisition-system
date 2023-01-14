#include "nrf24.hpp"

#include <iostream>
#include <thread>

#include "debug.hpp"

uint8_t addresses[2][6] = {"1Node", "2Node"};
// TODO: Don't hardcode radio number
bool radio_number = false; // Indexes above array

Nrf24Radio::Nrf24Radio()
{
    std::cout << "Starting NRF24 Radio..." << std::endl;

    // TODO: Don't hardcode this configuration
    this->nrf24_ = RF24(25, 0, 100000);

    if (!this->nrf24_.begin())
        throw "NRF24 begin failed. Check wiring?";

    this->nrf24_.setPayloadSize(PACKET_LENGTH);
    // TODO: Test with high power level (potential power supply issues)
    this->nrf24_.setPALevel(RF24_PA_LOW);
    this->nrf24_.openWritingPipe(addresses[radio_number]);
    this->nrf24_.openReadingPipe(1, addresses[!radio_number]);

    this->nrf24_.startListening();

    debug << "Starting ZetaRf worker thread..." << std::endl;
    this->worker_ = std::thread(&Nrf24Radio::rx_tx_loop, this);

    std::cout << "NRF24 init done." << std::endl;

    this->nrf24_.printPrettyDetails();
}

void Nrf24Radio::loop_tick()
{
    if (this->nrf24_.available())
    {
        uint8_t packet_bytes[PACKET_LENGTH];
        this->nrf24_.read(packet_bytes, PACKET_LENGTH);
        auto packet_frame = reinterpret_cast<const Frame *>(packet_bytes);
        debug << "Packet received: " << &*packet_frame << std::endl;
        this->on_receive_(*packet_frame);
    }
}

/**
 * Calculate ellapsed time in microseconds.
 * Adapted from "getting started" rf24 example
 */
uint32_t getMicros(timespec startTimer)
{
    // this function assumes that the timer was started using
    // `clock_gettime(CLOCK_MONOTONIC_RAW, &startTimer);`

    struct timespec endTimer;
    clock_gettime(CLOCK_MONOTONIC_RAW, &endTimer);
    uint32_t seconds = endTimer.tv_sec - startTimer.tv_sec;
    uint32_t useconds = (endTimer.tv_nsec - startTimer.tv_nsec) / 1000;

    return ((seconds)*1000 + useconds) + 0.5;
}

void Nrf24Radio::transmit_packet(const Frame packet)
{
    this->nrf24_.stopListening();

    struct timespec startTimer;
    clock_gettime(CLOCK_MONOTONIC_RAW, &startTimer);

    const int max_attemps = 3;
    for (int attempt = 0; attempt < max_attemps; attempt++)
    {
        if (this->nrf24_.write(&packet, PACKET_LENGTH))
        {
            auto timerEllapsed = getMicros(startTimer);
            debug << "Packet transmitted in " << timerEllapsed << " us." << std::endl;
            break;
        }
        else
        {
            debug << "Failed to send packet. ("
                  << attempt + 1
                  << "/"
                  << max_attemps
                  << ")"
                  << std::endl;
        }
    }

    this->nrf24_.startListening();
}
