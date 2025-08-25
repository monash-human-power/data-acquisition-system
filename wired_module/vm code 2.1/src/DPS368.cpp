#include "DPS368.h"
#include <Arduino.h>
#include <math.h>

bool DPS368::is_coef_ready() {
    read_sensor_register(DPS368_MEAS_CFG, 1, 1000);
    return (readBuffer[0] & 0x08); // coefficient ready bit
}

bool DPS368::is_sensor_ready() {
    read_sensor_register(DPS368_MEAS_CFG, 1, 1000);
    return (readBuffer[0] & 0x04); // sensor ready bit
}

void DPS368::get_coef_source() {
    read_sensor_register(DPS368_COEF_SRCE, 1, 1000);
    coef_source = readBuffer[0] & 0x80;
}

uint32_t DPS368::get_scale_factor(uint8_t oversamplingRate) {
    switch (oversamplingRate) {
        case 1: return 524288;
        case 2: return 1572864;
        case 8: return 3670016;
        case 16: return 7864320;
        case 32: return 253952;
        case 64: return 1040384;
        case 128: return 2088960;
        default: return 524288;
    }
}

void DPS368::read_coefficients() {
    read_sensor_register(DPS368_COEF, 3, 1000);
    c0 = convert_two_complement((readBuffer[0] << 4) | (readBuffer[1] >> 4), 12);
    c1 = convert_two_complement(((readBuffer[1] & 0x0F) << 8) | readBuffer[2], 12);

    read_sensor_register(DPS368_COEF + 3, 5, 1000);
    c00 = convert_two_complement((readBuffer[0] << 12) | (readBuffer[1] << 4) | (readBuffer[2] >> 4), 20);
    c10 = convert_two_complement(((readBuffer[2] & 0x0F) << 16) | (readBuffer[3] << 8) | readBuffer[4], 20);
}

void DPS368::select_mode(DPS368Mode mode) {
    write_sensor_register(DPS368_MEAS_CFG, (uint8_t)mode, 1000);
}

int32_t DPS368::read_raw_temperature() {
    read_sensor_register(DPS368_TMP, 3, 1000);
    int32_t rawTemp = (readBuffer[0] << 16) | (readBuffer[1] << 8) | readBuffer[2];
    return convert_two_complement(rawTemp, 24);
}

int32_t DPS368::read_raw_pressure() {
    read_sensor_register(DPS368_PSR, 3, 1000);
    int32_t rawPressure = (readBuffer[0] << 16) | (readBuffer[1] << 8) | readBuffer[2];
    return convert_two_complement(rawPressure, 24);
}

void DPS368::calculate_temperature() {
    float rawTemp = read_raw_temperature() / float(get_scale_factor(TMP_OVERSAMPLING_RATE));
    temperature = c0 * 0.5f + c1 * rawTemp;
}

void DPS368::calculate_pressure() {
    float rawTemp = read_raw_temperature() / float(get_scale_factor(TMP_OVERSAMPLING_RATE));
    float rawPressure = read_raw_pressure() / float(get_scale_factor(PSR_OVERSAMPLING_RATE));
    pressure = c00 + rawPressure * (c10 + rawPressure * (c20 + rawPressure * c30))
               + rawTemp * c01 + rawTemp * rawPressure * (c11 + rawPressure * c21);
}

void DPS368::configure() {
    read_sensor_register(DPS368_PRODUCT_ID, 1, 1000);
    if (readBuffer[0] != DPS368_ID) {
        Serial.println("DPS368 not found!");
        return;
    }
    Serial.println("DPS368 found");

    while (!is_sensor_ready()); // optional: add timeout
    while (!is_coef_ready());

    get_coef_source();
    read_coefficients();

    write_sensor_register(DPS368_PRS_CFG, PSR_CONFIG, 1000);
    write_sensor_register(DPS368_TMP_CFG, coef_source + TMP_CONFIG, 1000);

    select_mode(CON_BOTH);
}

void DPS368::read() {
    calculate_pressure();
    calculate_temperature();
}

String DPS368::generateJson() {
    return "{\"sensors\":[{\"type\":\"dps368\",\"temperature\":" +
           String(temperature, 2) + ",\"pressure\":" + String(pressure, 2) + "}]}";
}

void DPS368::send() {
    sendJson(sensorID, generateJson());
}
