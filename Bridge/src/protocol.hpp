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
