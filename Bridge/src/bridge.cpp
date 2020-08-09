#include "bridge.hpp"

const std::string Bridge::MQTT_HASH_SEPARATOR = "ZetaBridgeSeparator";

Bridge::Bridge(MqttBridgeClient_ptr mqttClient)
    : mqtt_client_(mqttClient)
{
    using namespace std::placeholders;
    this->mqtt_client_->set_on_message(std::bind(&Bridge::mqttMessageReceivedCallback, this, _1));
    this->zeta_radio_->set_on_received(std::bind(&Bridge::zetaRfPacketReceivedCallback, this, _1));
}

void Bridge::mqttMessageReceivedCallback(mqtt::const_message_ptr message)
{
    auto hash = this->hashMqttMessage(message);
    if (this->recently_sent_messages_.contains(hash))
        // This message was sent from us (the bridge), so discard
        return;

    const auto packets = this->tx_.packMessage(message);
    this->zeta_radio_->send_packets(packets);
}

void Bridge::zetaRfPacketReceivedCallback(const Frame packet)
{
    if (auto message = this->rx_.receivePacket(packet))
    {
        // Store the hash of this message so we know to discard it when receive
        // it back from the broker
        const auto hash = this->hashMqttMessage(*message);
        this->recently_sent_messages_.put(hash);

        this->mqtt_client_->publish(*message);
    }
}

size_t Bridge::hashMqttMessage(mqtt::const_message_ptr message) const
{
    static const std::hash<std::string> str_hash;
    // Separate the topic from the payload so that topic=AB and message=C has
    // a different hash to topic=A message=BC.
    const auto key = message->get_topic() + Bridge::MQTT_HASH_SEPARATOR + message->get_payload();
    return str_hash(key);
}
