#include <DPS368.h>

/*
Check if the DSP368's coefficient register is available. (Max 40ms - Section 3.6 of the Datasheet)
TODO: in the future the is_coef_ready() and is_sensor_ready() could be combine since they are 
reading from the same register */
boolean DPS368::is_coef_ready(){
    read_sensor_register(DPS368_MEAS_CFG,1,1000);
    // Bit 7 of the MEAS_CFG register is the COEF_RDY
    return (this->readBuffer[0] & 0x128);
}

/*
Check if the DPS368's preasure sensor is completely initialised. (Max 12ms - Section 3.6 of the Datasheet)
It is recommend not to start measurements until the sensor has
completed the self intialisation.*/ 
boolean DPS368::is_sensor_ready(){
    read_sensor_register(DPS368_MEAS_CFG,1,1000);

    // Bit 6 of the MEAS_CFG register is the SENSOR_RDY
    return (this->readBuffer[0] & 0x64);
}

/*
(section 8.12 of the datasheet)
Temperature coefficients are based on:
0 - Internal temperature sensor (of ASIC)
1 - External temperature sensor (of pressure sensor MEMS element)
*/
uint8_t DPS368::get_coef_source(){
    read_sensor_register(DPS368_COEF_SRCE,1,1000);
    this->coef_source = this->readBuffer[0] & 0x80; // get the most significant bit
}

// TODO: 
void DPS368::get_coefficient(){

    // //c0 and c1
    // read_sensor_register(DPS368_COEF,3,1000);

    // int16_t c0 = ((uint16_t)this->readBuffer[0] << 4) | (this->readBuffer[1] >> 4);
    // int16_t c1 = ((uint16_t)this->readBuffer[1] << 8) | this->readBuffer[2];

}

void DPS368::select_mode(DPS368Mode measurementMode){
    write_sensor_register(DPS368_MEAS_CFG,(int) measurementMode,1000);
}

// TODO:
// read the raw temperature and process it to get the actual temperature
void DPS368::read_temperature(){
    return ;
}

void DPS368::read_pressure(){
    return ;
}

void DPS368::configure(){

    // Check product ID to validate if the sensor is connected to I2C
    read_sensor_register(DPS368_PRODUCT_ID, 1,1000);
    if (this->readBuffer[0] == DPS368_ID){
        printf("DPS368 found\n");
    } else {
        printf("DPS368 not found\n");
        return ; // TODO: return error code
    }

    // blocks until the sensor is initialised and coefficient is available
    while(!this->is_sensor_ready());
    while(!this->is_coef_ready()); 

    this->get_coef_source();

    // Get the coefficient, do we need to get coef every time? or its it just constant everytime
    this->get_coefficient();
     
    // Set measurement rate and oversampling rate
    write_sensor_register(DPS368_PRS_CFG,PSR_CONFIG,1000);
    write_sensor_register(DPS368_TMP_CFG,coef_source+TMP_CONFIG,1000);

    // Set operating mode 
    this->select_mode(CON_BOTH);
}

void DPS368::read(){
    // Read temperature
    this -> read_temperature();
    this -> read_pressure();
}
