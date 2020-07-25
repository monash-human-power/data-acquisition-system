#include "protocol.hpp"

#include <algorithm>
#include <iomanip>
#include <iostream>

std::ostream& operator<<(std::ostream& os, Frame *frame)
{
    os << std::hex;

    auto bytes = reinterpret_cast<uint8_t *>(frame);
    for (size_t i = 0; i < sizeof(*frame); i++)
        os << std::setfill('0') << std::setw(2) << (int) bytes[i] << " ";

    os << std::dec;

    return os;
}

RxProtocol::RxProtocol(void (*received_callback)(std::vector<uint8_t>))
{
    this->m_on_received = received_callback;
}

void RxProtocol::reset()
{
    this->body.clear();
    this->m_next_part_count = 0;
}

void RxProtocol::receivePacket(const uint8_t *packet)
{
    auto frame = reinterpret_cast<const Frame *>(packet);

    if (frame->frame_type != FrameType::Message)
        // Not implemented
        return;

    if (frame->frame_counter != this->m_next_frame_count)
        // We must have skipped a frame, discard everything
        this->reset();
    this->m_next_frame_count++;

    if (frame->part_counter == 0)
    {
        // Starting new message
        this->reset();
        this->m_remaining_body_bytes = frame->body_length;
    } else if (frame->part_counter != this->m_next_part_count)
    {
        // We're resuming a message but dropped a packet, unrecoverable
        // Reset will occur when we next successfully start a new message
        return;
    }
    this->m_next_part_count++;

    // Read frame body
    uint16_t bytes_to_read = std::min(this->m_remaining_body_bytes, BODY_LENGTH);
    for (size_t i = 0; i < bytes_to_read; i++)
        this->body.push_back(frame->body[i]);
    this->m_remaining_body_bytes -= bytes_to_read;

    if (this->m_remaining_body_bytes == 0)
    {
        // Full message has been received
        this->m_on_received(this->body);
        this->reset();
    }
}