#include <iostream>
#include <thread>

#include "mqtt.hpp"

MqttCallback::MqttCallback(mqtt::async_client_ptr client)
    : client_(client) {}

void MqttCallback::set_on_message(std::function<void(mqtt::const_message_ptr)> callback)
{
    this->on_message_ = callback;
}

void MqttCallback::on_failure(const mqtt::token& asyncActionToken)
{
    std::cout << "MQTT connection failed" << std::endl;
    exit(1);
}

// Either this or connected() may be used
void MqttCallback::on_success(const mqtt::token& asyncActionToken) {}

void MqttCallback::connected(const std::string& cause)
{
    std::cout << "MQTT connection succeeded" << std::endl;
    this->client_->subscribe("#", 0);
}

void MqttCallback::connection_lost(const std::string& cause)
{
    std::cout << "MQTT connection lost" << std::endl;
}

void MqttCallback::message_arrived(mqtt::const_message_ptr message)
{
    this->on_message_(message);
}


MqttBridgeClient::MqttBridgeClient(std::string broker_address)
{
    const auto client_id = this->generate_client_id();
    this->client_ = std::make_shared<mqtt::async_client>(broker_address, client_id);

    mqtt::connect_options conn_opts;
    conn_opts.set_keep_alive_interval(20);
    conn_opts.set_clean_session(true);
    conn_opts.set_automatic_reconnect(MIN_RECONNECT_INTERVAL, MAX_RECONNECT_INTERVAL);

    this->callback_ = std::make_shared<MqttCallback>(this->client_);
    this->client_->set_callback(*callback_);

    try
    {
        // Connect to client
        std::cout << "Connecting to MQTT broker..." << std::endl;
        this->client_->connect(conn_opts);
    }
    catch (const mqtt::exception& exc)
    {
        std::cerr << "MQTT Error: " << exc.what() << " ["
            << exc.get_reason_code() << "]" << std::endl;
    }
}

MqttBridgeClient::~MqttBridgeClient()
{
    // Disconnect MQTT client
    this->client_->disconnect()->wait();
}

void MqttBridgeClient::set_on_message(std::function<void(mqtt::const_message_ptr)> callback)
{
    this->callback_->set_on_message(callback);
}

void MqttBridgeClient::publish(mqtt::const_message_ptr message) const
{
    // Wait until a connection is established before publishing
    // TODO: Add to a send queue instead to avoid blocking
    while (!this->client_->is_connected())
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    this->client_->publish(message);
}

std::string MqttBridgeClient::generate_client_id() const
{
    // Generate client_id identically to paho-mqtt python library
    constexpr size_t LENGTH = 23;
    std::string prefix("paho/");

    srand(time(nullptr));
    auto randchar = []() -> char
    {
        const char charset[] = "0123456789ADCDEF";
        const size_t max_index = (sizeof(charset) - 1);
        return charset[rand() % max_index];
    };
    std::string str(LENGTH - prefix.size(), 0);
    std::generate_n(str.begin(), LENGTH - prefix.size(), randchar);

    return prefix + str;
}
