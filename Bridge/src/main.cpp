#include <iostream>

#include "bridge.hpp"
#include "mqtt.hpp"
#include "nrf24.hpp"

struct Args
{
    bool is_bike = false;
    std::string broker_address = "tcp://localhost:1883";
    bool bike_wiring = false;
};

std::optional<Args> get_args(int argc, char *argv[])
{
    Args args;

    if (argc < 2)
        return args;

    std::string first_arg = argv[1];

    bool help_requested = first_arg == "-h" || first_arg == "--help";
    bool valid_device = first_arg == "bike" || first_arg == "chase";

    if (help_requested || !valid_device || argc > 4)
    {
        std::cout << "Usage: " << argv[0] << " [-h] [bike|chase] [BROKER_ADDRESS] [pin-bike|pin-chase]\n"
                                             "  -h, --help      show this help message and exit\n"
                                             "  bike|chase      whether this is the bike or chase car (default)\n"
                                             "  BROKER_ADDRESS  the MQTT broker address, optionally including port or protocol.\n"
                                             "                  (optional, defaults to 'localhost')\n"
                                             "  pin-bike|pin-chase Whether the radio is connected in the bike or chase car wiring configuration.\n";
        return {};
    }

    args.is_bike = first_arg == "bike";

    if (argc >= 3)
    {
        args.broker_address = argv[2];
    }
    if (argc >= 4)
    {
        std::string bikeWiring = argv[3]; // Need to convert to std::string to compare
        if(bikeWiring == "pin-bike") {
            args.bike_wiring = true;
        }
    }
    return args;
}

int main(int argc, char *argv[])
{
    auto args = get_args(argc, argv);
    if (!args)
        return 1;

    // Set the pinout
    // Default to chase car.
    uint16_t pin_ce;
    uint16_t pin_cs;
    if ((*args).bike_wiring)
    {
        pin_ce = 0;
        pin_cs = 12; // spidev1.2
        std::cout << "Using the bike wiring configuration";
    }
    else
    {
        pin_ce = 25;
        pin_cs = 0; //spidev0.0
        std::cout << "Using the chase car wiring configuration";
    }
    printf(" (ce=%d, cs=%d)\n", pin_ce, pin_cs);

    auto mqttClient = std::make_shared<MqttBridgeClient>((*args).broker_address);
    auto radio = std::make_shared<Nrf24Radio>((*args).is_bike, pin_ce, pin_cs);
    Bridge bridge(mqttClient, radio);

    while (std::cin.get() != 'q')
    {
        // Seems to always be running when running as a service, so only check every so often.
        std::this_thread::sleep_for(std::chrono::milliseconds(1000));
    }

    return 0;
}
