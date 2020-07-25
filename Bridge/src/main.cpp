#include <iostream>
#include <iomanip>

#include "protocol.hpp"

void receive_callback(std::vector<uint8_t> bytes)
{
    std::cout << "Received a message:" << std::endl << std::hex;
    for (auto &&byte : bytes)
        std::cout << std::setfill('0') << std::setw(2) << (int) byte << " ";
    std::cout << std::dec << std::endl;
    
}

int main() {
    std::cout << "Hello world!" << std::endl;

    TxProtocol tx;

    auto message1 = tx.packPackets(std::vector<uint8_t>({4, 5, 6}));

    std::vector<uint8_t> big_body;
    for (uint8_t i = 0; i < 128; i++)
        big_body.push_back(i);
    auto message2 = tx.packPackets(big_body);
    auto message3 = tx.packPackets(big_body);

    RxProtocol rx(receive_callback);

    rx.receivePacket(reinterpret_cast<uint8_t *>(&message1[0]));
    rx.receivePacket(reinterpret_cast<uint8_t *>(&message2[0]));
    rx.receivePacket(reinterpret_cast<uint8_t *>(&message2[1])); // Valid up to here
    rx.receivePacket(reinterpret_cast<uint8_t *>(&message3[1])); // Skipped a packet
}