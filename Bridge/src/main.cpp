#include <iostream>

#include "mqtt.hpp"
#include "protocol.hpp"

int main()
{
    auto mqttClient = std::make_shared<MqttBridgeClient>();
    Protocol protocol(mqttClient);

    while (std::cin.get() != 'q')
        ;

    return 0;
}
