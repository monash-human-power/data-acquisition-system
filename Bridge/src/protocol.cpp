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

Protocol::Protocol(std::function<void(mqtt::message_ptr)> mqtt_pub_func)
    : mqtt_pub_func_(mqtt_pub_func) { }

void Protocol::reset()
{
    this->rxState_.body.clear();
    this->rxState_.next_part_count = 0;
}

void Protocol::receivePacket(const uint8_t *packet)
{
    const auto frame = reinterpret_cast<const Frame *>(packet);

    if (frame->frame_type != FrameType::Message)
        // Not implemented
        return;

    if (frame->frame_counter != this->rxState_.next_frame_count)
        // We must have skipped a frame, discard everything
        this->reset();
    this->rxState_.next_frame_count++;

    if (frame->part_counter == 0)
    {
        // Starting new message
        this->reset();
        this->rxState_.remaining_body_bytes = frame->body_length;
    } else if (frame->part_counter != this->rxState_.next_part_count)
    {
        // We're resuming a message but dropped a packet, unrecoverable
        // Reset will occur when we next successfully start a new message
        return;
    }
    this->rxState_.next_part_count++;

    // Read frame body
    const auto bytes_to_read = std::min(this->rxState_.remaining_body_bytes, BODY_LENGTH);
    for (size_t i = 0; i < bytes_to_read; i++)
        this->rxState_.body.push_back(frame->body[i]);
    this->rxState_.remaining_body_bytes -= bytes_to_read;

    if (this->rxState_.remaining_body_bytes == 0)
    {
        // Full message has been received
        this->parse_mqtt_message();
        this->reset();
    }
}

void Protocol::parse_mqtt_message()
{
    if (this->rxState_.body.size() < 2)
    {
        std::cerr << "Failed to parse packet body: "
                     "Body is too small to contain required data" << std::endl;
        return;
    }

    auto body_iterator = this->rxState_.body.begin();

    const auto qos_retained_bits = *body_iterator++;
    const auto qos = qos_retained_bits & QOS_MASK;
    const bool retained = qos_retained_bits & RETAIN_MASK;

    const auto topic_size = *body_iterator++;

    if (std::distance(body_iterator, this->rxState_.body.end()) < topic_size)
    {
        std::cerr << "Failed to pase packet body: "
                     "Topic size is too large to fit in body" << std::endl;
        return;
    }

    const std::string topic(body_iterator, body_iterator + topic_size);
    body_iterator += topic_size;

    const std::string payload(body_iterator, this->rxState_.body.end());

    try
    {
        auto message = mqtt::make_message(topic, payload, qos, retained);
        this->mqtt_pub_func_(message);
    }
    catch(const mqtt::exception& exc)
    {
        std::cerr << "mqtt::exception thrown while sending MQTT message: "
            << exc.what() << std::endl;
    }
}


std::vector<Frame> Protocol::packPackets(const std::vector<uint8_t> body)
{
    std::vector<Frame> frames;
    uint8_t next_part_count = 0;

    for (size_t i = 0; i < body.size(); i += BODY_LENGTH)
    {
        auto last = std::min(body.size(), i + BODY_LENGTH);

        Frame frame;
        frame.frame_counter = this->txState_.next_frame_count++;
        frame.frame_type = FrameType::Message;
        frame.part_counter = next_part_count++;
        frame.body_length = body.size();
        std::copy(body.begin() + i, body.begin() + last, frame.body);

        frames.push_back(frame);
    }

    return frames;
}
