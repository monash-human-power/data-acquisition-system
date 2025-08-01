#include "SpiMaster.h"


/*
#define MOSI_PIN        13
#define MISO_PIN        12
#define SCLK_PIN        14

*/

#define SPI_MODE        0

           
SpiMaster::SpiMaster(spi_host_device_t host, int mosi, int miso, int sclk) {

    esp_err_t ret;

   // Configure bus settings for communication
   spi_bus_config_t masterConfig = {
    .mosi_io_num = mosi,
    .miso_io_num = miso,
    .sclk_io_num = sclk,
    .quadwp_io_num =  -1, // write protect -- not used
    .quadhd_io_num = -1 // hold signal -- not used
   };

   // Initialise bus  
    ret = spi_bus_initialize(host, &masterConfig, SPI_DMA_CH_AUTO);
    ESP_ERROR_CHECK(ret);

};

// Adding sub-devices (sensors)

void SpiMaster::add_device(spi_host_device_t host, uint32_t clockSpeedHz, int csPin, spi_device_handle_t* handle){

   

   // Configure the device interface with specific CS pin - for each sensor

   spi_device_interface_config_t deviceConfig = {
    .mode = SPI_MODE,  
    .clock_speed_hz = clockSpeedHz,
    .spics_io_num = csPin, // chip select for device,
    .queue_size = 1 
   };

    // Call add_device function
    ESP_ERROR_CHECK(spi_bus_add_device(this->host, &deviceConfig, handle));

   

};

