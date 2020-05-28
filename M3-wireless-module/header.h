
/**************************************************************************/
// Add this file to your arduino folder before compilation
/**************************************************************************/
#ifndef header_h
#define header_h

#include "Arduino.h"

// CO2 Sensor parameters
#define RLOAD 10.0
#define RZERO 18.35
#define PARA 116.6020682
#define PARB 2.769034857

// Parameters to model temperature and humidity dependence
#define CORA 0.00035
#define CORB 0.02718
#define CORC 1.39538
#define CORD 0.0018

// Atmospheric CO2 level for calibration purposes
#define ATMOCO2 400

// GPS pins
#define RXD2 16
#define TXD2 17

// CO2 sensor class
class MQ135 {
 private:
  int _pin;

 public:
  MQ135(int pin);
  float getCorrectionFactor(float t, float h);
  float getResistance();
  float getCorrectedResistance(float t, float h);
  float getPPM();
  float getCorrectedPPM(float t, float h);
  float getRZero();
  float getCorrectedRZero(float t, float h);
};

#endif