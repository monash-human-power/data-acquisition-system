#include <iomanip>
#include <ostream>
#include <stdint.h>
#include <vector>

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

class RxProtocol
{
public:
    RxProtocol(void (*received_callback)(std::vector<uint8_t>));

    void receivePacket(const uint8_t *packet);

private:
    void reset();

    uint8_t m_frame_count = 0;
    uint8_t m_part_count = 0;

    std::vector<uint8_t> body;
    uint8_t m_remaining_body_bytes;

    void (*m_on_received)(std::vector<uint8_t>);
};

class TxProtocol
{
public:
    TxProtocol();

    std::vector<Frame> packPackets(std::vector<uint8_t> body);

private:
    uint8_t m_frame_count = 0;
    uint8_t m_part_count = 0;
};
