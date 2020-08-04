#include "protocol.hpp"

#include <algorithm>
#include <iostream>
#include <iterator>

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

    if (!this->next_frame_count_)
    {
        // This is the first packet to be received, start the frame counting
        this->next_frame_count_ = packet.frame_counter + 1;
    } else if (packet.frame_counter != this->next_frame_count_)
    {
        // We must have skipped a frame, discard everything
        this->reset();
        this->next_frame_count_ = packet.frame_counter + 1;
    } else
    {
        // Normal case, increment for next frame
        (*this->next_frame_count_)++;
    }

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
    this->body_.insert(this->body_.end(), &packet.body[0], &packet.body[bytes_to_read]);
    this->remaining_body_bytes_ -= bytes_to_read;

    if (this->remaining_body_bytes_ == 0)
    {
        // Full message has been received
        auto message = this->deserialiseMqttMessage();
        this->reset();
        return message;
    }
    return { };
}

std::optional<mqtt::message_ptr> RxProtocol::deserialiseMqttMessage()
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


std::vector<Frame> TxProtocol::packMessage(mqtt::const_message_ptr message)
{
    auto bytes = this->serialiseMessage(message);

    std::vector<Frame> frames;
    uint8_t next_part_count = 0;

    for (size_t i = 0; i < bytes.size(); i += BODY_LENGTH)
    {
        auto last = std::min(bytes.size(), i + BODY_LENGTH);

        Frame frame;
        frame.frame_counter = this->next_frame_count_++;
        frame.frame_type = FrameType::Message;
        frame.part_counter = next_part_count++;
        frame.body_length = bytes.size();
        std::copy(bytes.begin() + i, bytes.begin() + last, frame.body);

        frames.push_back(frame);
    }

    return frames;
}

std::vector<uint8_t> TxProtocol::serialiseMessage(mqtt::const_message_ptr message)
{
    std::vector<uint8_t> bytes;
    auto inserter = back_inserter(bytes);

    uint8_t qos_retained_bits = message->get_qos() | (uint8_t) message->is_retained() << 2;
    inserter = qos_retained_bits; // This operation inserts

    auto topic = message->get_topic();
    bytes.push_back(topic.size());
    std::copy(topic.begin(), topic.end(), inserter);

    auto payload = message->get_payload();
    std::copy(payload.begin(), payload.end(), inserter);

    return bytes;
}

const std::string Protocol::MQTT_HASH_SEPARATOR = "ZetaBridgeSeparator";

Protocol::Protocol(MqttBridgeClient_ptr mqttClient)
    : mqtt_client_(mqttClient)
{
    using namespace std::placeholders;
    this->mqtt_client_->set_on_message(std::bind(&Protocol::mqttMessageReceivedCallback, this, _1));
    this->zeta_radio_->set_on_received(std::bind(&Protocol::zetaRfPacketReceivedCallback, this, _1));
}

void Protocol::mqttMessageReceivedCallback(mqtt::const_message_ptr message)
{
    auto hash = this->hashMqttMessage(message);
    if (this->recently_sent_messages_.contains(hash))
        // This message was sent from us (the bridge), so discard
        return;

    auto packets = this->tx_.packMessage(message);
    this->zeta_radio_->send_packets(packets);
}

void Protocol::zetaRfPacketReceivedCallback(const Frame packet)
{
    if (auto message = this->rx_.receivePacket(packet))
    {
        // Store the hash of this message so we know when we receive it back from the broker
        auto hash = this->hashMqttMessage(*message);
        this->recently_sent_messages_.put(hash);
        this->mqtt_client_->publish(*message);
    }
}

size_t Protocol::hashMqttMessage(mqtt::const_message_ptr message) const
{
    std::hash<std::string> str_hash;
    auto key = message->get_topic() + Protocol::MQTT_HASH_SEPARATOR + message->get_payload();
    return str_hash(key);
}
