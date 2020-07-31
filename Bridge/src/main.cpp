#include <iostream>
#include <iomanip>

#include "mqtt/async_client.h"

#include "protocol.hpp"
#include "mqtt.hpp"

void receive_callback(mqtt::message_ptr message)
{
    std::cout << "Parsed packet!" << std::endl
        << "\tQoS:      " << message->get_qos() << std::endl
        << "\tRetained: " << message->is_retained() << std::endl
        << "\tTopic:    " << message->get_topic() << std::endl
        << "\tPayload:  " << message->get_payload() << std::endl;
}

int main()
{
    using namespace std::placeholders; // for `_1`

    std::cout << "Hello world!" << std::endl;


    ////////////// MQTT //////////////

    MqttBridgeClient mqttClient;

    ////////////// PROTOCOL //////////////

    Protocol protocol(std::bind(&MqttBridgeClient::publish, &mqttClient, _1));

    // QOS: 0, Retain: false, Topic: "AB", Payload: "CD"
    auto message = protocol.packPackets(std::vector<uint8_t>(
        { 0b0000'0000, 2, 'A', 'B', 'C', 'D' }
    ));

    protocol.receivePacket(message[0]);

    while (std::cin.get() != 'q')
        ;

    return 0;
}
