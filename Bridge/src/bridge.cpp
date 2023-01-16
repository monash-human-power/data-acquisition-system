#include "bridge.hpp"

const std::string Bridge::MQTT_HASH_SEPARATOR = "ZetaBridgeSeparator";

Bridge::Bridge(MqttBridgeClient_ptr mqttClient)
    : mqtt_client_(mqttClient)
{
    using namespace std::placeholders;
    this->mqtt_client_->set_on_message(std::bind(&Bridge::mqtt_message_received_callback, this, _1));
    this->zeta_radio_->set_on_received(std::bind(&Bridge::zetarf_packet_received_callback, this, _1));
}

void Bridge::mqtt_message_received_callback(mqtt::const_message_ptr message)
{
    auto hash = this->hash_mqtt_message(message);
    if (this->recently_sent_messages_.contains(hash))
        // This message was sent from us (the bridge), so discard
        return;

    const auto packets = this->tx_.pack_message(message);
    this->zeta_radio_->send_packets(packets);
}

void Bridge::zetarf_packet_received_callback(const Frame packet)
{
    if (auto message = this->rx_.receive_packet(packet))
    {
        // Store the hash of this message so we know to discard it when receive
        // it back from the broker
        const auto hash = this->hash_mqtt_message(*message);
        this->recently_sent_messages_.put(hash);

        this->mqtt_client_->publish(*message);
    }
}

size_t Bridge::hash_mqtt_message(mqtt::const_message_ptr message) const
{
    static const std::hash<std::string> str_hash;
    // Separate the topic from the payload so that topic=AB and message=C has
    // a different hash to topic=A message=BC.
    const auto key = message->get_topic() + Bridge::MQTT_HASH_SEPARATOR + message->get_payload();
    return str_hash(key);
}
