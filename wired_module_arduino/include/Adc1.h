#include "driver/adc.h"
#include "SensorBase.h"

#ifndef ADC
#define ADC

class Adc1: public SensorBase {

    public:
        // Constructor
        Adc1(adc1_channel_t adcChannel, adc_atten_t attenuation, adc_bits_width_t bitWidth,uint8_t sensorID);
        
        // Methods
        void configure() override ;
        void read() override ;     
    
    private:
        // Attributes
        adc1_channel_t adcChannel;
        adc_atten_t attenuation;
        adc_bits_width_t bitWidth;

};

#endif