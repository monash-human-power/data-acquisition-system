#include "driver/spi_master.h" 

#ifndef SPI_MASTER
#define SPI_MASTER

class SpiMaster {

    public:
    // Attributes
    spi_host_device_t host;  // Store host as an attribute for reuse

    // Cnstructor
    SpiMaster(spi_host_device_t host, int mosi, int miso, int sclk);
    
    // Deconstructor
    ~SpiMaster();

    // Add sub-device (subsequent sensors)
    void add_device(uint32_t clockSpeedHz, int csPin, spi_device_handle_t* handle);

    void add_device(spi_host_device_t host, uint32_t clock_speed_hz, int cs_pin, spi_device_t** device_handle);

};

#endif

