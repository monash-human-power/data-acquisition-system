#include <iostream>

#include "protocol.hpp"

int main() {
    std::cout << "Hello world!" << std::endl;

    Frame frame{1, FrameType::Message, 2, 3, {4, 5}};

    std::cout << sizeof(frame) << std::endl;
    std::cout << &frame << std::endl;
}