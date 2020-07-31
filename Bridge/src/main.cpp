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

int main() {
    std::cout << "Hello world!" << std::endl;


    ////////////// MQTT //////////////

    MqttBridgeClient mqttClient;

    ////////////// PROTOCOL //////////////

    TxProtocol tx;
    RxProtocol rx(receive_callback);

    // QOS: 1, Retain: true, Topic: "AB", Payload: "CD"
    auto message1 = tx.packPackets(std::vector<uint8_t>(
        { 0b0000'0101, 2, 'A', 'B', 'C', 'D' }
    ));
    // QOS: 3 (INVALID), Retain: false, Topic: "wxyz", Payload: ""
    auto message2 = tx.packPackets(std::vector<uint8_t>(
        { 0b0000'0011, 4, 'w', 'x', 'y', 'z' }
    ));

    rx.receivePacket(reinterpret_cast<uint8_t *>(&message1[0]));
    rx.receivePacket(reinterpret_cast<uint8_t *>(&message2[0]));

    while (std::cin.get() != 'q')
        ;

    return 0;
}
