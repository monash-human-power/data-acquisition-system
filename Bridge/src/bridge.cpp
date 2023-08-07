#include "bridge.hpp"

const std::string Bridge::MQTT_HASH_SEPARATOR = "RadioBridgeSeparator";

Bridge::Bridge(MqttBridgeClient_ptr mqttClient, Radio_ptr radio)
    : mqtt_client_(mqttClient), radio_(radio)
{
    using namespace std::placeholders;
    this->mqtt_client_->set_on_message(std::bind(&Bridge::mqtt_message_received_callback, this, _1));
    this->radio_->set_on_received(std::bind(&Bridge::radio_packet_received_callback, this, _1));
}

void Bridge::mqtt_message_received_callback(mqtt::const_message_ptr message)
{
    debug << "Bridge got an MQTT message" << std::endl;
    auto hash = this->hash_mqtt_message(message);
    if (this->recently_sent_messages_.contains(hash))
    {
        // This message was sent from us (the bridge), so discard
        return;
    }
    if ((message->get_topic().find("mpu_data") != std::string::npos) || (message->get_topic().find("crash_detection") != std::string::npos) || (message->get_topic().find("strain_gauge") != std::string::npos))
    {
        // This message is on the banned topics list. Don't send it across.
        // Useful for excluding high data rate messages that the receiver isn't
        // interested in.
        // TODO: Make this more flexible than hardcoded.
        debug << "Dropping message of banned topic" << std::endl;
        return;
    }
    const auto packets = this->tx_.pack_message(message);
    this->radio_->send_packets(packets);
}

void Bridge::radio_packet_received_callback(const Frame packet)
{
    debug << "Bridge got a radio message" << std::endl;
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
