#include "nrf24.hpp"

#include <iostream>
#include <thread>

#include "debug.hpp"

uint8_t addresses[2][6] = {"1Node", "2Node"};
bool radio_number = false; // Indexes above array

Nrf24Radio::Nrf24Radio()
{
    std::cout << "Starting NRF24 Radio..." << std::endl;

    if (!this->nrf24_.begin())
        throw "NRF24 begin failed. Check wiring?";

    this->nrf24_.setPayloadSize(PACKET_LENGTH);
    // TODO: Test with high power level (potential power supply issues)
    this->nrf24_.setPALevel(RF24_PA_LOW);
    this->nrf24_.openWritingPipe(addresses[radio_number]);
    this->nrf24_.openReadingPipe(1, addresses[!radio_number]);

    debug << "Starting ZetaRf worker thread..." << std::endl;
    this->worker_ = std::thread(&Nrf24Radio::rx_tx_loop, this);

    std::cout << "NRF24 init done." << std::endl;
}
