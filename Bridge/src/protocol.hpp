#pragma once

#include <optional>
#include <ostream>
#include <stdint.h>
#include <vector>

#include <mqtt/message.h>

#include "mqtt.hpp"
#include "ring_buffer.hpp"

constexpr uint16_t BODY_LENGTH = 75;
constexpr uint16_t PACKET_LENGTH = 80;

constexpr uint8_t QOS_MASK    = 0b0000'0011;
constexpr uint8_t RETAIN_MASK = 0b0000'0100;

constexpr size_t MESSAGE_HISTORY = 50;

enum class FrameType : uint8_t
{
    Message = 0,
};

struct __attribute__((packed)) Frame
{
    uint8_t frame_counter;
    FrameType frame_type;
    uint8_t part_counter;
    uint16_t body_length;
    uint8_t body[BODY_LENGTH] = {0};
};

std::ostream& operator<<(std::ostream& os, const Frame *frame);

class RxProtocol
{
public:
    std::optional<mqtt::message_ptr> receivePacket(const Frame packet);

private:
    void reset();
    std::optional<mqtt::message_ptr> deserialiseMqttMessage();

    // Don't start the frame count from 0, as the other end of the bridge may
    // have already started sending packets
    std::optional<uint8_t> next_frame_count_ = std::nullopt;
    uint8_t next_part_count_ = 0;

    std::vector<uint8_t> body_;
    uint16_t remaining_body_bytes_ = 0;
};

class TxProtocol
{
public:
    std::vector<Frame> packMessage(mqtt::const_message_ptr message);

private:
    uint8_t next_frame_count_ = 0;

    std::vector<uint8_t> serialiseMessage(mqtt::const_message_ptr message);
};

class Protocol
{
    RxProtocol rx_;
    TxProtocol tx_;

    MqttBridgeClient_ptr mqtt_client_;

    RingBuffer<size_t, MESSAGE_HISTORY> recently_sent_messages_;

    static const std::string MQTT_HASH_SEPARATOR;

public: // TODO - only public for dev purposes
    void mqttMessageReceivedCallback(mqtt::const_message_ptr message);
    void zetaRfPacketReceivedCallback(const Frame packet);
private:

    size_t hashMqttMessage(mqtt::const_message_ptr message) const;

public:
    Protocol(MqttBridgeClient_ptr mqttClient);
};
