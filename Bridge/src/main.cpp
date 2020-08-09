#include <iostream>

#include "bridge.hpp"
#include "mqtt.hpp"

int main()
{
    auto mqttClient = std::make_shared<MqttBridgeClient>();
    Bridge bridge(mqttClient);

    while (std::cin.get() != 'q')
        ;

    return 0;
}
