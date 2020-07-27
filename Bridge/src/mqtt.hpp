#pragma once

#include "mqtt/async_client.h"

constexpr std::chrono::seconds MIN_RECONNECT_INTERVAL(1);
constexpr std::chrono::seconds MAX_RECONNECT_INTERVAL(20);

class MqttCallback : public virtual mqtt::callback,
                     public virtual mqtt::iaction_listener
{
public:
    using ptr_t = std::shared_ptr<MqttCallback>;

private:
    mqtt::async_client_ptr client_;

    void on_failure(const mqtt::token& asyncActionToken) override;
    void on_success(const mqtt::token& asyncActionToken) override;

    void connected(const std::string& cause) override;
    void connection_lost(const std::string& cause) override;
    void message_arrived(mqtt::const_message_ptr msg) override;

public:
    MqttCallback(mqtt::async_client_ptr client, mqtt::connect_options &conn_opts);
};

using MqttCallback_ptr = MqttCallback::ptr_t;

class MqttBridgeClient
{
private:
    mqtt::async_client_ptr client_;
    MqttCallback_ptr callback_;

    std::string generate_client_id();

public:
    MqttBridgeClient();
    ~MqttBridgeClient();
};
