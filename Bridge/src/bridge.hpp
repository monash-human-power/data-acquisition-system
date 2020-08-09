#pragma once

#include "protocol.hpp"

/**
 * Manages and runs the MQTT Bridge.
 */
class Bridge
{
    /** Handles converting radio packets to MQTT messages. */
    RxProtocol rx_;
    /** Handles converting MQTT messages to radio packets. */
    TxProtocol tx_;

    /**
     * The MQTT client to publish messages from the radio module on, and
     * receive messages for radio transmission with.
     */
    MqttBridgeClient_ptr mqtt_client_;
    /**
     * The Zeta radio to transmit all received MQTT messages with, and from
     * which to receive packets for publishing to MQTT.
     */
    ZetaRfRadio_ptr zeta_radio_ = std::make_shared<ZetaRfRadio>();

    /**
     * Contains the hashes of recent messages.
     * This is used to compare incoming MQTT messages to the ones this class
     * published, so that we don't send the same MQTT messages back and forth
     * over the bridge indefinitely. If an incoming message matches one
     * recently published, it will not be sent.
     */
    RingBuffer<size_t, MESSAGE_HISTORY> recently_sent_messages_;

    /**
     * Separates the topic from the payload when hashing mqtt messages.
     * @see hash_mqtt_message.
     */
    static const std::string MQTT_HASH_SEPARATOR;

    /** Transmit an MQTT message by radio (if it is not one we published). */
    void mqtt_message_received_callback(mqtt::const_message_ptr message);
    /** Process a received radio packet for publishing. */
    void zetarf_packet_received_callback(const Frame packet);

    /**
     * Compute a hash of an MQTT message which will be unique for a unique
     * topic and payload.
     * @param message The MQTT message to hash.
     * @return The hash of the MQTT message.
     */
    size_t hash_mqtt_message(mqtt::const_message_ptr message) const;

public:
    /**
     * Create a new Bridge to manage the MQTT radio bridge.
     * Will initialise the Zeta module and set up appropriate callbacks to
     * handle forwarding data between the Zeta radio and the supplied MQTT
     * client.
     * @param mqttClient The MQTT client to send/receive MQTT messages with.
     */
    Bridge(MqttBridgeClient_ptr mqttClient);
};