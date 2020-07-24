#include <iomanip>
#include <ostream>
#include <stdint.h>

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
    uint8_t body[75];
};

std::ostream& operator<<(std::ostream& os, Frame *frame)
{
    os << std::hex;

    auto bytes = reinterpret_cast<uint8_t *>(frame);
    for (size_t i = 0; i < sizeof(*frame); i++)
    {
        os << std::setfill('0') << std::setw(2) << (int) bytes[i] << " ";
    }
    
    os << std::dec;

    return os;
}