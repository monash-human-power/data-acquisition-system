#include "SPISensor.h"

SPISensor::SPISensor(std::string id, SPIBus& bus) : SensorBase(id), bus(bus) {
    // The bus is opened by the sensor's init()
};

SPISensor::~SPISensor(){
    // The bus is owned by whoever created it
};
