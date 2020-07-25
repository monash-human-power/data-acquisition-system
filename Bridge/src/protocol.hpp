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
    uint8_t body[BODY_LENGTH];
};

std::ostream& operator<<(std::ostream& os, Frame *frame);

class RxProtocol
{
public:
    RxProtocol(void (*received_callback)(std::vector<uint8_t>));

    void receivePacket(const uint8_t *packet);

private:
    void reset();

    uint8_t m_next_frame_count = 0;
    uint8_t m_next_part_count = 0;

    std::vector<uint8_t> body;
    uint16_t m_remaining_body_bytes = 0;

    void (*m_on_received)(std::vector<uint8_t>);
};

class TxProtocol
{
public:
    TxProtocol();

    std::vector<Frame> packPackets(std::vector<uint8_t> body);

private:
    uint8_t m_next_frame_count = 0;
    uint8_t m_next_part_count = 0;
};
