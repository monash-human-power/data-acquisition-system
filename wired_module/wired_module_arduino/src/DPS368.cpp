#include <DPS368.h>

/*
Check if the DSP368's coefficient register is available. (Max 40ms - Section 3.6 of the Datasheet)
TODO: in the future the is_coef_ready() and is_sensor_ready() could be combine since they are 
reading the same register */
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

// TODO: 
void DPS368::get_coefficient(){

}

void DPS368::select_mode(DPS368Mode measurementMode){
    write_sensor_register(DPS368_MEAS_CFG,(int) measurementMode,1000);
}

void DPS368::configure(){

    // Check product ID to validate if the sensor is connected to I2C
    read_sensor_register(DPS368_PRODUCT_ID, 1,1000);
    if (this->readBuffer[0] == DPS368_ID){
        printf("DPS368 found\n");
    } else {
        printf("DPS368 not found\n");
        return ;
    }

    // blocks until the sensor is initialised and coefficient is available
    while(!this->is_sensor_ready());
    while(!this->is_coef_ready()); 
    
    // Set oversampling 
    // Set operating mode 
    this->select_mode(CON_BOTH);
        
    
    
}

void DPS368::read(){

}
