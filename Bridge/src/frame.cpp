#include "frame.hpp"

std::ostream& operator<<(std::ostream& os, const Frame *frame)
{
    os << std::hex;

    const auto bytes = reinterpret_cast<const uint8_t *>(frame);
    for (size_t i = 0; i < sizeof(*frame); i++)
        os << std::setfill('0') << std::setw(2) << (int) bytes[i] << " ";

    os << std::dec;

    return os;
}