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

void RxProtocol::reset()
{
    this->body_.clear();
    this->next_part_count_ = 0;
}

std::optional<mqtt::message_ptr> RxProtocol::receivePacket(const Frame packet)
{
    if (packet.frame_type != FrameType::Message)
        // Not implemented
        return { };

    if (packet.frame_counter != this->next_frame_count_)
        // We must have skipped a frame, discard everything
        this->reset();
    this->next_frame_count_++;

    if (packet.part_counter == 0)
    {
        // Starting new message
        this->reset();
        this->remaining_body_bytes_ = packet.body_length;
    } else if (packet.part_counter != this->next_part_count_)
    {
        // We're resuming a message but dropped a packet, unrecoverable
        // Reset will occur when we next successfully start a new message
        return { };
    }
    this->next_part_count_++;

    // Read frame body
    const auto bytes_to_read = std::min(this->remaining_body_bytes_, BODY_LENGTH);
    for (size_t i = 0; i < bytes_to_read; i++)
        this->body_.push_back(packet.body[i]);
    this->remaining_body_bytes_ -= bytes_to_read;

    if (this->remaining_body_bytes_ == 0)
    {
        // Full message has been received
        auto message = this->parse_mqtt_message();
        this->reset();
        return { message };
    }
    return { };
}

std::optional<mqtt::message_ptr> RxProtocol::parse_mqtt_message()
{
    if (this->body_.size() < 2)
    {
        std::cerr << "Failed to parse packet body: "
                     "Body is too small to contain required data" << std::endl;
        return { };
    }

    auto body_iterator = this->body_.begin();

    const auto qos_retained_bits = *body_iterator++;
    const auto qos = qos_retained_bits & QOS_MASK;
    const bool retained = qos_retained_bits & RETAIN_MASK;

    const auto topic_size = *body_iterator++;

    if (std::distance(body_iterator, this->body_.end()) < topic_size)
    {
        std::cerr << "Failed to pase packet body: "
                     "Topic size is too large to fit in body" << std::endl;
        return { };
    }

    const std::string topic(body_iterator, body_iterator + topic_size);
    body_iterator += topic_size;

    const std::string payload(body_iterator, this->body_.end());

    try
    {
        return { mqtt::make_message(topic, payload, qos, retained) };
    }
    catch(const mqtt::exception& exc)
    {
        std::cerr << "mqtt::exception thrown while sending MQTT message: "
            << exc.what() << std::endl;
        return { };
    }
}


std::vector<Frame> TxProtocol::packPackets(const std::vector<uint8_t> body)
{
    std::vector<Frame> frames;
    uint8_t next_part_count = 0;

    for (size_t i = 0; i < body.size(); i += BODY_LENGTH)
    {
        auto last = std::min(body.size(), i + BODY_LENGTH);

        Frame frame;
        frame.frame_counter = this->next_frame_count_++;
        frame.frame_type = FrameType::Message;
        frame.part_counter = next_part_count++;
        frame.body_length = body.size();
        std::copy(body.begin() + i, body.begin() + last, frame.body);

        frames.push_back(frame);
    }

    return frames;
}
