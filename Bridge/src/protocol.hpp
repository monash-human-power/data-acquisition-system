#pragma once

#include <optional>
#include <stdint.h>
#include <vector>

#include <mqtt/message.h>

#include "frame.hpp"
#include "mqtt.hpp"
#include "ring_buffer.hpp"
#include "zeta.hpp"

/** The bits used by QOS in the qos/retain byte. */
constexpr uint8_t QOS_MASK    = 0b0000'0011;
/** The bits used by retain in the qos/retain byte. */
constexpr uint8_t RETAIN_MASK = 0b0000'0100;

/**
 * The number of message hashes received over the radio to retain.
 */
constexpr size_t MESSAGE_HISTORY = 50;

/** Handles receiving packets/frames and parsing them into MQTT packets. */
class RxProtocol
{
public:
    /**
     * Process and incoming frame from the radio.
     * @param packet The incoming frame.
     * @return An MQTT message if the frame successfully completed the end of a
     *         message, otherwise std::nullopt.
     */
    std::optional<mqtt::message_ptr> receivePacket(const Frame packet);

private:
    /** Prepare to process a new message */
    void reset();
    /**
     * Parse the received bytes in this->body_ into an MQTT message.
     * @return The parsed MQTT message if successful, otherwise std::nullopt.
     */
    std::optional<mqtt::message_ptr> deserialiseMqttMessage();

    /**
     * The frame count we expect the next received packet to contain.
     * The frame count should start counting from the next received packet's
     * count, as the other end of the bridge may have already started sending
     * packets before this end started listening.
     */
    std::optional<uint8_t> next_frame_count_ = { };
    /** The part count to expect the next frame to contain. */
    uint8_t next_part_count_ = 0;

    /** The accumulated body of the message currently being received. */
    std::vector<uint8_t> body_;
    /**
     * The number of bytes we still expect to receive for the current
     * message.
     */
    uint16_t remaining_body_bytes_ = 0;
};

/** Handles splitting up MQTT messages into a series of packets/frames. */
class TxProtocol
{
public:
    /**
     * Split an MQTT message into a series of packets.
     * @param message The MQTT message to process
     * @return A vector containing the corresponding packets. The first element
     *         should be the first to be sent by radio.
     */
    std::vector<Frame> packMessage(mqtt::const_message_ptr message);

private:
    /** The frame count for the next packet to be created. */
    uint8_t next_frame_count_ = 0;

    /**
     * Converts an MQTT message into a collection of bytes to be packed into
     * packets for transmission.
     * @param message The MQTT message to be processed.
     * @return The message serialised as a vector of bytes.
     */
    std::vector<uint8_t> serialiseMessage(mqtt::const_message_ptr message);
};

/**
 * Manages and runs the MQTT Bridge.
 */
class Protocol
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
     * @see hashMqttMessage.
     */
    static const std::string MQTT_HASH_SEPARATOR;

    /** Transmit an MQTT message by radio (if it is not one we published). */
    void mqttMessageReceivedCallback(mqtt::const_message_ptr message);
    /** Process a received radio packet for publishing. */
    void zetaRfPacketReceivedCallback(const Frame packet);

    /**
     * Compute a hash of an MQTT message which will be unique for a unique
     * topic and payload.
     * @param message The MQTT message to hash.
     * @return The hash of the MQTT message.
     */
    size_t hashMqttMessage(mqtt::const_message_ptr message) const;

public:
    /**
     * Create a new Protocol to manage the MQTT Bridge.
     * Will initialise the Zeta module and set up appropriate callbacks to
     * handle forwarding data between the Zeta radio and the supplied MQTT
     * client.
     * @param mqttClient The MQTT client to send/receive MQTT messages with.
     */
    Protocol(MqttBridgeClient_ptr mqttClient);
};
