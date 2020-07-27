#include <iostream>

#include "mqtt.hpp"

MqttCallback::MqttCallback(mqtt::async_client_ptr client, mqtt::connect_options& conn_opts)
    : client_(client) {}

void MqttCallback::on_failure(const mqtt::token& asyncActionToken)
{
    std::cout << "Connection failed" << std::endl;
    exit(1);
}

// Either this or connected() may be used
void MqttCallback::on_success(const mqtt::token& asyncActionToken) {}

void MqttCallback::connected(const std::string& cause)
{
    std::cout << "Connection success" << std::endl;
    this->client_->subscribe("#", 0);
}

void MqttCallback::message_arrived(mqtt::const_message_ptr msg)
{
    std::cout << "Received message on topic \"" << msg->get_topic() << "\"" << std::endl
        << "Payload:  " << msg->to_string() << std::endl
        << "QoS:      " << msg->get_qos() << std::endl
        << "Retained: " << msg->is_retained() << std::endl;
}


MqttBridgeClient::MqttBridgeClient()
{
    const auto client_id = this->generate_client_id();
    this->client_ = std::make_shared<mqtt::async_client>("tcp://localhost:1883", client_id);

    mqtt::connect_options conn_opts;
    conn_opts.set_keep_alive_interval(20);
    conn_opts.set_clean_session(true);

    this->callback_ = std::make_shared<MqttCallback>(this->client_, conn_opts);
    this->client_->set_callback(*callback_);

    try
    {
        // Connect to client
        std::cout << "Connecting..." << std::endl;
        this->client_->connect(conn_opts)->wait();
    }
    catch (const mqtt::exception& exc)
    {
        std::cerr << "Error: " << exc.what() << " ["
            << exc.get_reason_code() << "]" << std::endl;
    }
}

MqttBridgeClient::~MqttBridgeClient()
{
    // Disconnect MQTT client
    this->client_->disconnect()->wait();
}

std::string MqttBridgeClient::generate_client_id()
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
