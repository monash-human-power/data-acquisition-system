#include "debug.hpp"

class NullBuffer : public std::streambuf
{
public:
    int overflow(int c)
    {
        return c;
    }
};

NullBuffer null_buffer;
std::ostream null_stream(&null_buffer);
