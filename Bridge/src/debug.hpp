#pragma once

#include <iostream>

/**
 * A stream which may be used just like std::cout but does nothing with its
 * input i.e. does not print
 */
extern std::ostream null_stream;

#if defined(MQTT_BRIDGE_DEBUG)
    #define debug std::cout
#else
    #define debug null_stream
#endif