// #include "hal/adc_types.h"
// #include "esp_adc/adc_oneshot.h"


// void app_main() {

//     adc_oneshot_unit_handle_t adc2_handle;
//     adc_oneshot_unit_init_cfg_t init_config1 = {
//         .unit_id = ADC_UNIT_2,
//         .ulp_mode = ADC_ULP_MODE_DISABLE,
//     };

//     adc_oneshot_chan_cfg_t config = {
//     .bitwidth = ADC_BITWIDTH_12,
//     .atten = ADC_ATTEN_DB_12,
//     };

//     ESP_ERROR_CHECK(adc_oneshot_new_unit(&init_config1, &adc2_handle));

//     int rawADC;

//     ESP_ERROR_CHECK(adc_oneshot_config_channel(adc2_handle,ADC_CHANNEL_0, &config));

//     while (1){
//         ESP_ERROR_CHECK(adc_oneshot_read(adc2_handle, ADC_CHANNEL_0,&rawADC));
//         printf("ADC value: %d\n", rawADC);
//         vTaskDelay(1000 / portTICK_PERIOD_MS);
//     }

//     ESP_ERROR_CHECK(adc_oneshot_del_unit(adc2_handle));


// }

#include "driver/adc.h"
#include "freertos/FreeRTOS.h"

void app_main() {
    adc1_config_width(ADC_WIDTH_BIT_12);
    adc1_config_channel_atten(ADC1_CHANNEL_0, ADC_ATTEN_DB_12);
    
    while (1) {
        int val = adc1_get_raw(ADC1_CHANNEL_0);
        printf("ADC value: %d\n", val);
        vTaskDelay(1000 / portTICK_PERIOD_MS);
    }
}