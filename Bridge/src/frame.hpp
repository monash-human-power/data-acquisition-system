#pragma once

#include <iomanip>
#include <iostream>
#include <ostream>
#include <stdint.h>

/** Size of the packet body in bytes. */
constexpr uint16_t BODY_LENGTH = 75;
/** Total size of the packet in bytes. */
constexpr uint16_t PACKET_LENGTH = 80;

/**
 * Types of packets that may be transmitted and received.
 * The associated value is the ID of the frame type which is sent as part of
 * the packet.
 */
enum class FrameType : uint8_t
{
    Message = 0,
};

/**
 * The format of a message frame.
 * Each part of the frame appears in the order it is shown below with no
 * packaging. Everything uses little endian encoding under ARM and x86.
 */
struct __attribute__((packed)) Frame
{
    /** Total number of frames sent, modulo 255. */
    uint8_t frame_count;
    /** Type of the frame. Currently always FrameType::Message. */
    FrameType frame_type;
    /** Position of the frame within a message, modulo 255. */
    uint8_t part_count;
    /** Length of the message body across all frames. */
    uint16_t body_length;
    /** A slice of the body content, up to 75 bytes in length, zero padded. */
    uint8_t body[BODY_LENGTH] = {0};
};

/**
 * Writes the bytes of a Frame to an ostream. Useful for printing the frame's
 * contents.
 */
std::ostream& operator<<(std::ostream& os, const Frame *frame);
