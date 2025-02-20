#include <DPS368.h>

void DPS368::configure(){
    read_sensor_register(DPS368_PRODUCT_ID, 1,1000);
    if (this->readBuffer[0] == DPS368_ID) printf("DPS368 found\n");
    else printf("DPS368 not found\n");
    
    
}

void DPS368::read(){

}
