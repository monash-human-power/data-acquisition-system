#pragma once

#include <iomanip>
#include <iostream>
#include <ostream>
#include <stdint.h>

constexpr uint16_t BODY_LENGTH = 75;
constexpr uint16_t PACKET_LENGTH = 80;

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
