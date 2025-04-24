#include "Adc1.h"
#include <cstring>
#include <Arduino.h>

Adc1::Adc1(adc1_channel_t adcChannel, adc_atten_t attenuation, 
           adc_bits_width_t bitWidth, uint8_t canId)
    : SensorBase(canId), adcChannel(adcChannel), 
      attenuation(attenuation), bitWidth(bitWidth) {}

void Adc1::configure() {
    adc1_config_width(bitWidth);
    adc1_config_channel_atten(adcChannel, attenuation); 
}

void Adc1::read() {
    int rawVal = adc1_get_raw(adcChannel);
    float val = 3.3 * rawVal / 4095.0f;
    memcpy(this->canBuffer, &val, sizeof(val));
}

void Adc1::send() {
    float voltage = *((float*)this->canBuffer);

    String json = generateJson(voltage);
    sendJson(this->canId, json);  // Uses the inherited CAN ID
}

String Adc1::generateJson(float voltage) {
    return "{\"sensors\":[{\"type\":\"adc1\",\"voltage\":" + String(voltage, 3) + "}]}";
}
