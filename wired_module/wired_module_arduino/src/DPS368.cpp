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
uint32_t DPS368::get_scale_factor(uint8_t oversamplingRate){
    uint32_t scaleFactor;
    switch(oversamplingRate){
        case 1:
            scaleFactor = 524288;
            break;
        case 2:
            scaleFactor = 1572864;
            break;
        case 8:
            scaleFactor = 3670016;
            break;
        case 16:
            scaleFactor = 7864320; 
            break;
        case 32:
            scaleFactor = 253952;
            break;
        case 64:
            scaleFactor = 1040384;
            break;
        case 128:
            scaleFactor = 2088960;
            break;
        default:
            scaleFactor = 253952; // scale factor for oversampling of 16 times (standard)   
    }
    return scaleFactor;
}

// TODO: 
void DPS368::get_coefficient(){

    //c0 and c1
    read_sensor_register(DPS368_COEF,3,1000);

    c0 = ((uint16_t)this->readBuffer[0] << 4) | (this->readBuffer[1] >> 4);
    c0 = convert_two_complement(c0,12);
    c1 = ((uint16_t)this->readBuffer[1] << 8) | this->readBuffer[2];
    c1 = convert_two_complement(c1,12);

    //c00 and c10
    read_sensor_register(DPS368_COEF+3,5,1000);
    
    c00 = ((uint32_t)this->readBuffer[0] << 12) | ((uint32_t)this->readBuffer[1] << 4) | (this->readBuffer[2] >> 4);
    c00 = convert_two_complement(c00,20);
    c10 = ((uint32_t)(this->readBuffer[2] & 0x0F) << 16) | ((uint32_t)this->readBuffer[3] << 8) | this->readBuffer[4];
    c10 = convert_two_complement(c10,20);

    //c01
    read_sensor_register(DPS368_COEF+8,2,1000);
    
    c01 = ((uint16_t)this->readBuffer[0] << 8) | this->readBuffer[1];
    c01 = convert_two_complement(c01,16);

    //c11
    read_sensor_register(DPS368_COEF+10,2,1000);
    c11 = ((uint16_t)this->readBuffer[0] << 8) | this->readBuffer[1];
    c11 = convert_two_complement(c11,16);

    //c20
    read_sensor_register(DPS368_COEF+12,2,1000);
    c20 = ((uint16_t)this->readBuffer[0] << 8) | this->readBuffer[1];
    c20 = convert_two_complement(c20,16);

    //c21 
    read_sensor_register(DPS368_COEF+14,2,1000);
    c21 = ((uint16_t)this->readBuffer[0] << 8) | this->readBuffer[1];
    c21 = convert_two_complement(c21,16);

    //c30
    read_sensor_register(DPS368_COEF+16,2,1000);
    c30 = ((uint16_t)this->readBuffer[0] << 8) | this->readBuffer[1];
    c30 = convert_two_complement(c30,16);
}

void DPS368::select_mode(DPS368Mode measurementMode){
    write_sensor_register(DPS368_MEAS_CFG,(int) measurementMode,1000);
}

int32_t DPS368::read_raw_temperature(){
    read_sensor_register(DPS368_TMP,3,1000);
    
    int32_t rawTemp = ((uint32_t)this->readBuffer[0] << 16) | ((uint16_t)this->readBuffer[1] << 8) | this->readBuffer[2];
    rawTemp = convert_two_complement(rawTemp,24);     
    rawTemp /= get_scale_factor(TMP_OVERSAMPLING_RATE);
    
    return rawTemp;
}

// read the raw temperature and process it to get the actual temperature
void DPS368::caculate_temperature(){
    int32_t rawTemp = read_raw_temperature();
    int32_t temp = c0*0.5 + c1*rawTemp;
}

int32_t DPS368::read_raw_pressure(){
    read_sensor_register(DPS368_PSR,3,1000);
    int32_t rawPressure = ((uint32_t)this->readBuffer[0] << 16) | ((uint16_t)this->readBuffer[1] << 8) | this->readBuffer[2];

    rawPressure = convert_two_complement(rawPressure,24);
    rawPressure /= get_scale_factor(PSR_OVERSAMPLING_RATE);
    return rawPressure;
}
void DPS368::calculate_pressure(){
    int32_t rawTemp = read_raw_temperature();
    int32_t rawPressure = read_raw_pressure();

    int32_t pressure = c00 + rawPressure*(c10 + rawPressure*(c20 + rawPressure*c30)) 
                        + rawTemp*c01 + rawTemp*rawPressure*(c11+ rawPressure*c21);

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
    this -> calculate_pressure();
    this -> caculate_temperature();
}
