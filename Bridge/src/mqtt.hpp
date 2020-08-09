#pragma once

#include <functional>

#include "mqtt/async_client.h"

/** The minimum time between attempts to reconnect to the MQTT broker */
constexpr std::chrono::seconds MIN_RECONNECT_INTERVAL(1);
/** The maximum time between attempts to reconnect to the MQTT broker */
constexpr std::chrono::seconds MAX_RECONNECT_INTERVAL(20);

/**
 * A class to handle callbacks from the paho.mqtt.cpp library.
 * Does not need to be used outside of mqtt.hpp/mqtt.cpp.
 */
class MqttCallback : public virtual mqtt::callback,
                     public virtual mqtt::iaction_listener
{
public:
    /** Smart/shared pointer to this class. */
    using ptr_t = std::shared_ptr<MqttCallback>;

private:
    /** Reference to the paho MQTT client. */
    mqtt::async_client_ptr client_;

    /** Function to be called when an MQTT message is received. */
    std::function<void(mqtt::const_message_ptr)> on_message_;

    /** Invoked when some action fails. */
    void on_failure(const mqtt::token& asyncActionToken) override;
    /** Invoked when some action (e.g. connecting) completes successfully. */
    void on_success(const mqtt::token& asyncActionToken) override;

    /**
     * Invoked when we successfully connect to the MQTT broker.
     * Will subscribe to all topics ("#").
     */
    void connected(const std::string& cause) override;
    /** Invoked when we loose connection to the MQTT broker */
    void connection_lost(const std::string& cause) override;
    /**
     * Invoked when receive a message the MQTT broker.
     * This will call the externally-specified on_message_ callback.
     * @param message The MQTT message which has been received.
     */
    void message_arrived(mqtt::const_message_ptr message) override;

public:
    /**
     * Create a new instance of MqttCallback.
     * Upon successful connection, a subscription will be made to "#".
     * @param client The MQTT client that will use the callbacks provided by
     *               this class.
     */
    MqttCallback(mqtt::async_client_ptr client);

    /**
     * Set the function to be called when an MQTT message is received.
     * @param callback The callback function.
     */
    void set_on_message(std::function<void(mqtt::const_message_ptr)> callback);
};

/** Smart/shared pointer to an MqttCallback */
using MqttCallback_ptr = MqttCallback::ptr_t;

class MqttBridgeClient
{
public:
    /** Smart/shared pointer to this class. */
    using ptr_t = std::shared_ptr<MqttBridgeClient>;

private:
    /** The paho.mqtt.cpp client. */
    mqtt::async_client_ptr client_;
    /** Class which manages all callback events for the client. */
    MqttCallback_ptr callback_;

    /**
     * Generates a random client ID using the same format as the paho-mqtt
     * python library.
     */
    std::string generate_client_id() const;

    /** Class is non-copyable. */
    MqttBridgeClient(const MqttBridgeClient& that) = delete;
    MqttBridgeClient& operator=(const MqttBridgeClient& that) = delete;

public:
    /**
     * Create a new MqttBrideClient. Will attempt to connect to the localhost
     * MQTT broker on creation.
     */
    MqttBridgeClient();
    /**
     * Disconnect from the MQTT client.
     */
    ~MqttBridgeClient();

    /**
     * Set the function to be called when an MQTT message is received.
     * @param callback The callback function.
     */
    void set_on_message(std::function<void(mqtt::const_message_ptr)> callback);

    /**
     * Publish a pre-existing MQTT messsage.
     * Will block until the MQTT client is connected to the broker.
     * @param message The message to be sent.
     */
    void publish(mqtt::const_message_ptr message) const;
};

/** Smart/shared pointer to an MqttBridgeClient */
using MqttBridgeClient_ptr = MqttBridgeClient::ptr_t;