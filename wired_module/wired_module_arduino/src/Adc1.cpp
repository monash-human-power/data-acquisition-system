#include "Adc1.h"

Adc1::Adc1(adc1_channel_t adcChannel, adc_atten_t attenuation, 
                    adc_bits_width_t bitWidth, uint8_t sensorID) {
    
    this->adcChannel = adcChannel;
    this->attenuation = attenuation;
    this->bitWidth = bitWidth;
    this->sensorID = sensorID;
}

void Adc1::configure() {
    adc1_config_width(bitWidth);
    adc1_config_channel_atten(adcChannel, attenuation); 
}

void Adc1::read() {
    int rawVal = adc1_get_raw(adcChannel);
    float val = 3.3*rawVal/4095;
    memcpy(this->canBuffer, &val, sizeof(val));
}
