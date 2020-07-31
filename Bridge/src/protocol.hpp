#pragma once

#include <functional>
#include <ostream>
#include <stdint.h>
#include <vector>

#include <mqtt/message.h>

constexpr uint16_t BODY_LENGTH = 75;

constexpr uint8_t QOS_MASK    = 0b0000'0011;
constexpr uint8_t RETAIN_MASK = 0b0000'0100;

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
    RxProtocol(std::function<void(mqtt::message_ptr)> mqtt_pub_func_);

    void receivePacket(const uint8_t *packet);

private:
    void reset();
    void parse_mqtt_message();

    uint8_t next_frame_count_ = 0;
    uint8_t next_part_count_ = 0;

    std::vector<uint8_t> body_;
    uint16_t remaining_body_bytes_ = 0;

    std::function<void(mqtt::message_ptr)> mqtt_pub_func_;
};

class TxProtocol
{
public:
    std::vector<Frame> packPackets(const std::vector<uint8_t> body);

private:
    uint8_t next_frame_count_ = 0;
};
