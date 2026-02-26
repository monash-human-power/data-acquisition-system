#include "TwaiNode.h"

#define TX_GPIO GPIO_NUM_17
#define RX_GPIO GPIO_NUM_18
#define TX_QUEUE_DEPTH 1000

extern "C" void app_main(void) {
    //Start twai node
    TwaiNode twaiNode1(TX_GPIO,RX_GPIO,500000,TX_QUEUE_DEPTH);
    twaiNode1.register_event_callbacks();
    // twaiNode1.configure_timing();
    twaiNode1.enable_node();

    //create transmission frame
    uint64_t sensorData = 0;
    twai_frame_t txFrame = {
        .buffer = (uint8_t *) &sensorData,
        .buffer_len = sizeof(sensorData),
    };
    txFrame.header.id = 0x0;
    
    while(1) {
        twaiNode1.send_message(txFrame);
    }
    ESP_LOGI("esp32_node","Closing node");
}