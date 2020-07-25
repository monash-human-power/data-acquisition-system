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

    Frame frame1{0, FrameType::Message, 0, 79, {4, 5, 6}}; // Send 2 frame message
    Frame frame2{1, FrameType::Message, 1, 79, {4, 5, 6}};
    Frame frame3{2, FrameType::Message, 0, 5, {4, 5, 6}}; // Send single frame message
    Frame frame4{4, FrameType::Message, 0, 100, {4, 5, 6}}; // Skips frame but new message, will process
    Frame frame5{7, FrameType::Message, 1, 100, {4, 5, 6}}; // Skiped frame but part count is correct; Discard prev and this

    RxProtocol rx(receive_callback);

    auto bytes = reinterpret_cast<uint8_t *>(&frame1);
    rx.receivePacket(bytes);
    bytes = reinterpret_cast<uint8_t *>(&frame2);
    rx.receivePacket(bytes);
    bytes = reinterpret_cast<uint8_t *>(&frame3);
    rx.receivePacket(bytes);
    bytes = reinterpret_cast<uint8_t *>(&frame4);
    rx.receivePacket(bytes);
    bytes = reinterpret_cast<uint8_t *>(&frame5);
    rx.receivePacket(bytes);
}