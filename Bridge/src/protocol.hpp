#pragma once

#include <ostream>
#include <stdint.h>
#include <vector>

constexpr uint16_t BODY_LENGTH = 75;

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
    RxProtocol(void (*received_callback)(std::vector<uint8_t>));

    void receivePacket(const uint8_t *packet);

private:
    void reset();

    uint8_t next_frame_count_ = 0;
    uint8_t next_part_count_ = 0;

    std::vector<uint8_t> body_;
    uint16_t remaining_body_bytes_ = 0;

    void (*on_received_)(std::vector<uint8_t>);
};

class TxProtocol
{
public:
    std::vector<Frame> packPackets(const std::vector<uint8_t> body);

private:
    uint8_t next_frame_count_ = 0;
};
