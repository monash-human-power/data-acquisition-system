#include "GpsSensor.h"
#include <Arduino.h>
#include <cstring>

GpsSensor::GpsSensor(int uartNum, int rxPin, int txPin, uint8_t canId)
    : SensorBase(canId), uartNum(uartNum), rxPin(rxPin), txPin(txPin) {
    if (uartNum == 1) gpsSerial = &Serial1;
    else if (uartNum == 2) gpsSerial = &Serial2;
    else gpsSerial = &Serial;
}

void GpsSensor::configure() {
    gpsSerial->begin(9600, SERIAL_8N1, rxPin, txPin);
}

void GpsSensor::read() {
    static String gpsLine = "";

    while (gpsSerial->available()) {
        char c = gpsSerial->read();
        if (c == '\n') {
            gpsLine.trim();
            if (gpsLine.startsWith("$GPGGA")) {
                // Parse latitude and longitude
                String fields[15];
                int fieldIndex = 0;

                for (int i = 0; i < gpsLine.length(); i++) {
                    if (gpsLine[i] == ',' || i == gpsLine.length() - 1) {
                        fieldIndex++;
                    } else {
                        fields[fieldIndex] += gpsLine[i];
                    }
                }

                float lat = fields[2].toFloat();
                float lon = fields[4].toFloat();
                if (fields[3] == "S") lat = -lat;
                if (fields[5] == "W") lon = -lon;

                float data[2] = { lat, lon };
                memcpy(this->canBuffer, data, sizeof(data));
            }
            gpsLine = "";
        } else {
            gpsLine += c;
        }
    }
}
