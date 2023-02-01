#include <iostream>

#include "bridge.hpp"
#include "mqtt.hpp"
#include "nrf24.hpp"

struct Args
{
    bool is_bike = false;
    std::string broker_address = "tcp://localhost:1883";
};

std::optional<Args> get_args(int argc, char *argv[])
{
    Args args;

    if (argc < 2)
        return args;

    std::string first_arg = argv[1];

    bool help_requested = first_arg == "-h" || first_arg == "--help";
    bool valid_device = first_arg == "bike" || first_arg == "chase";

    if (help_requested || !valid_device || argc > 3)
    {
        std::cout << "Usage: " << argv[0] << " [-h] [bike|chase] [BROKER_ADDRESS]\n"
                                             "  -h, --help      show this help message and exit\n"
                                             "  bike|chase      whether this is the bike or chase car (default)\n"
                                             "  BROKER_ADDRESS  the MQTT broker address, optionally including port or protocol.\n"
                                             "                  (optional, defaults to 'localhost')\n";
        return {};
    }

    args.is_bike = first_arg == "bike";
    if (argc == 3)
        args.broker_address = argv[2];

    return args;
}

int main(int argc, char *argv[])
{
    auto args = get_args(argc, argv);
    if (!args)
        return 1;

    auto mqttClient = std::make_shared<MqttBridgeClient>((*args).broker_address);
    auto radio = std::make_shared<Nrf24Radio>((*args).is_bike, 25, 0);
    Bridge bridge(mqttClient, radio);

    while (std::cin.get() != 'q')
        ;

    return 0;
}
