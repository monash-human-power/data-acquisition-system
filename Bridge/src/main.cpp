#include <iostream>

#include "bridge.hpp"
#include "mqtt.hpp"

struct Args
{
    std::string broker_address = "tcp://localhost:1883";
};

std::optional<Args> get_args(int argc, char* argv[])
{
    Args args;

    if (argc < 2)
        return args;

    if (strcmp(argv[1], "--help") == 0 || strcmp(argv[1], "-h") == 0)
    {
        std::cout << "Usage: " << argv[0] << " [-h] [BROKER_ADDRESS]\n"
                     "  -h, --help      show this help message and exit\n"
                     "  BROKER_ADDRESS  the MQTT broker address, optionally including port or protocol.\n"
                     "                  (optional, defaults to 'localhost')\n";
        return { };
    }

    args.broker_address = argv[1];

    return args;
}

int main(int argc, char* argv[])
{
    auto args = get_args(argc, argv);
    if (!args)
        return 1;

    auto mqttClient = std::make_shared<MqttBridgeClient>((*args).broker_address);
    Bridge bridge(mqttClient);

    while (std::cin.get() != 'q')
        ;

    return 0;
}
