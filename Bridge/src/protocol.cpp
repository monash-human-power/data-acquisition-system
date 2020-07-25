#include "protocol.hpp"

#include <algorithm>
#include <iomanip>
#include <iostream>

std::ostream& operator<<(std::ostream& os, const Frame *frame)
{
    os << std::hex;

    const auto bytes = reinterpret_cast<const uint8_t *>(frame);
    for (size_t i = 0; i < sizeof(*frame); i++)
        os << std::setfill('0') << std::setw(2) << (int) bytes[i] << " ";

    os << std::dec;

    return os;
}

RxProtocol::RxProtocol(void (*received_callback)(std::vector<uint8_t>))
{
    this->on_received_ = received_callback;
}

void RxProtocol::reset()
{
    this->body_.clear();
    this->next_part_count_ = 0;
}

void RxProtocol::receivePacket(const uint8_t *packet)
{
    const auto frame = reinterpret_cast<const Frame *>(packet);

    if (frame->frame_type != FrameType::Message)
        // Not implemented
        return;

    if (frame->frame_counter != this->next_frame_count_)
        // We must have skipped a frame, discard everything
        this->reset();
    this->next_frame_count_++;

    if (frame->part_counter == 0)
    {
        // Starting new message
        this->reset();
        this->remaining_body_bytes_ = frame->body_length;
    } else if (frame->part_counter != this->next_part_count_)
    {
        // We're resuming a message but dropped a packet, unrecoverable
        // Reset will occur when we next successfully start a new message
        return;
    }
    this->next_part_count_++;

    // Read frame body
    const auto bytes_to_read = std::min(this->remaining_body_bytes_, BODY_LENGTH);
    for (size_t i = 0; i < bytes_to_read; i++)
        this->body_.push_back(frame->body[i]);
    this->remaining_body_bytes_ -= bytes_to_read;

    if (this->remaining_body_bytes_ == 0)
    {
        // Full message has been received
        this->on_received_(this->body_);
        this->reset();
    }
}