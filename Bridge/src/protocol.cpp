#include "protocol.hpp"

#include <algorithm>
#include <iostream>
#include <iterator>

#include "debug.hpp"

void RxProtocol::reset()
{
    this->body_.clear();
    this->next_part_count_ = 0;
}

std::optional<mqtt::message_ptr> RxProtocol::receive_packet(const Frame packet)
{
    if (packet.frame_type != FrameType::Message)
        // Not implemented
        return { };

    if (!this->next_frame_count_)
    {
        // This is the first packet to be received, start the frame counting
        this->next_frame_count_ = packet.frame_count + 1;
    } else if (packet.frame_count != this->next_frame_count_)
    {
        // We must have skipped a frame, discard everything
        this->reset();
        this->next_frame_count_ = packet.frame_count + 1;
        debug << "Frame skipped" << std::endl;
    } else
    {
        // Normal case, increment for next frame
        (*this->next_frame_count_)++;
    }

    if (packet.part_count == 0)
    {
        // Starting new message
        this->reset();
        this->remaining_body_bytes_ = packet.body_length;
    } else if (packet.part_count != this->next_part_count_)
    {
        // We're resuming a message but dropped a packet, unrecoverable
        // Reset will occur when we next successfully start a new message
        debug << "Part discarded due to previous skipped frame" << std::endl;
        return { };
    }
    this->next_part_count_++;

    // Read frame body
    const auto bytes_to_read = std::min(this->remaining_body_bytes_, BODY_LENGTH);
    this->body_.insert(this->body_.end(), &packet.body[0], &packet.body[bytes_to_read]);
    this->remaining_body_bytes_ -= bytes_to_read;

    if (this->remaining_body_bytes_ == 0)
    {
        // Full message has been received
        auto message = this->deserialise_mqtt_message();
        this->reset();
        return message;
    }
    return { };
}

std::optional<mqtt::message_ptr> RxProtocol::deserialise_mqtt_message()
{
    // The minimum body size is 2 bytes - one byte for QoS/retain and one more
    // to specify a zero topic length.
    if (this->body_.size() < 2)
    {
        std::cerr << "Failed to parse packet body: "
                     "Body is too small to contain required data" << std::endl;
        return { };
    }

    auto body_iterator = this->body_.begin();

    // Get QoS level and retained boolean
    const auto qos_retained_bits = *body_iterator++;
    const auto qos = qos_retained_bits & QOS_MASK;
    const bool retained = qos_retained_bits & RETAIN_MASK;

    // Get the length of the topic and check that it will fit in the body
    const auto topic_size = *body_iterator++;
    if (std::distance(body_iterator, this->body_.end()) < topic_size)
    {
        std::cerr << "Failed to parse packet body: "
                     "Topic size is too large to fit in body" << std::endl;
        return { };
    }

    // Get the topic
    const std::string topic(body_iterator, body_iterator + topic_size);
    body_iterator += topic_size;

    // Get the message payload
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


std::vector<Frame> TxProtocol::pack_message(mqtt::const_message_ptr message)
{
    // Convert the message to a collection of bytes
    const auto bytes = this->serialise_message(message);

    std::vector<Frame> frames;
    uint8_t next_part_count = 0;

    // Iterate through all the bytes of the message, but in chunks of however
    // many we are able to fit into the body of a single frame.
    for (size_t i = 0; i < bytes.size(); i += BODY_LENGTH)
    {
        // Last byte of the body to be included in this frame.
        // Fit up to BODY_LENGTH bytes but don't copy beyond the end of bytes.
        auto last = std::min(bytes.size(), i + BODY_LENGTH);

        // Create and populate frame
        Frame frame;
        frame.frame_count = this->next_frame_count_++;
        frame.frame_type = FrameType::Message;
        frame.part_count = next_part_count++;
        frame.body_length = bytes.size();
        std::copy(bytes.begin() + i, bytes.begin() + last, frame.body);

        frames.push_back(frame);
    }

    return frames;
}

std::vector<uint8_t> TxProtocol::serialise_message(mqtt::const_message_ptr message)
{
    std::vector<uint8_t> bytes;
    auto inserter = back_inserter(bytes);

    // Construct the byte containing the QoS and retain flag.
    uint8_t qos_retained_bits = message->get_qos() | (uint8_t) message->is_retained() << 2;
    bytes.push_back(qos_retained_bits);

    // Add topic size and content
    const auto topic = message->get_topic();
    bytes.push_back(topic.size());
    std::copy(topic.begin(), topic.end(), inserter);

    // Add message payload
    const auto payload = message->get_payload();
    std::copy(payload.begin(), payload.end(), inserter);

    return bytes;
}
