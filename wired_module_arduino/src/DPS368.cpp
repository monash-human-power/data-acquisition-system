#include <DPS368.h>
#include <ArduinoJson.h>  // Include ArduinoJson library for JSON handling

class DPS368 : public SensorBase {
public:
    // Coefficients for the DPS368 sensor
    int32_t c0, c1, c00, c10, c20, c30, c01, c11, c21;

    // Constructor
    DPS368(uint8_t sensorID) {
        this->sensorID = sensorID;  // Assign the sensor ID for this sensor
    }

    // Check if the coefficients are ready
    boolean is_coef_ready() {
        read_sensor_register(DPS368_MEAS_CFG, 1, 1000);
        return (this->readBuffer[0] & 0x128);  // Checking if coefficient data is ready
    }

    // Check if the sensor is ready
    boolean is_sensor_ready() {
        read_sensor_register(DPS368_MEAS_CFG, 1, 1000);
        return (this->readBuffer[0] & 0x64);  // Checking if the sensor is ready
    }

    // Get the coefficient source (whether temperature sensor is used or not)
    uint8_t get_coef_source() {
        read_sensor_register(DPS368_COEF_SRCE, 1, 1000);
        this->coef_source = this->readBuffer[0] & 0x80;  // Get the most significant bit to determine sensor mode
    }

    // Get scale factor based on oversampling rate
    uint32_t get_scale_factor(uint8_t oversamplingRate) {
        uint32_t scaleFactor;
        switch (oversamplingRate) {
            case 1: scaleFactor = 524288; break;
            case 2: scaleFactor = 1572864; break;
            case 8: scaleFactor = 3670016; break;
            case 16: scaleFactor = 7864320; break;
            case 32: scaleFactor = 253952; break;
            case 64: scaleFactor = 1040384; break;
            case 128: scaleFactor = 2088960; break;
            default: scaleFactor = 253952;  // Default scale factor
        }
        return scaleFactor;
    }

    // Get the coefficients from the sensor
    void get_coefficient() {
        read_sensor_register(DPS368_COEF, 3, 1000);  // Read the coefficients
        c0 = ((uint16_t)this->readBuffer[0] << 4) | (this->readBuffer[1] >> 4);  // Combine register data
        c0 = convert_two_complement(c0, 12);  // Apply two's complement if necessary
        c1 = ((uint16_t)this->readBuffer[1] << 8) | this->readBuffer[2];
        c1 = convert_two_complement(c1, 12);  // Apply two's complement if necessary

        // More coefficient calculations (c00, c10, etc.)
        read_sensor_register(DPS368_COEF + 3, 5, 1000);
        c00 = ((uint32_t)this->readBuffer[0] << 12) | ((uint32_t)this->readBuffer[1] << 4) | (this->readBuffer[2] >> 4);
        c00 = convert_two_complement(c00, 20);  // Apply two's complement to 20-bit values
        c10 = ((uint32_t)(this->readBuffer[2] & 0x0F) << 16) | ((uint32_t)this->readBuffer[3] << 8) | this->readBuffer[4];
        c10 = convert_two_complement(c10, 20);  // Apply two's complement to 20-bit values

        // Continue with the rest of the coefficients...
        // (c01, c11, c20, c21, c30, etc.)
    }

    // Select the measurement mode for the sensor
    void select_mode(DPS368Mode measurementMode) {
        write_sensor_register(DPS368_MEAS_CFG, (int) measurementMode, 1000);  // Set measurement mode
    }

    // Read the raw temperature value from the sensor
    int32_t read_raw_temperature() {
        read_sensor_register(DPS368_TMP, 3, 1000);  // Read temperature data
        int32_t rawTemp = ((uint32_t)this->readBuffer[0] << 16) | ((uint16_t)this->readBuffer[1] << 8) | this->readBuffer[2];
        rawTemp = convert_two_complement(rawTemp, 24);  // Apply two's complement
        rawTemp /= get_scale_factor(TMP_OVERSAMPLING_RATE);  // Apply scale factor
        return rawTemp;
    }

    // Calculate the actual temperature from the raw data
    void calculate_temperature() {
        int32_t rawTemp = read_raw_temperature();  // Get raw temperature data
        int32_t temp = c0 * 0.5 + c1 * rawTemp;  // Calculate temperature using the coefficients
    }

    // Read the raw pressure value from the sensor
    int32_t read_raw_pressure() {
        read_sensor_register(DPS368_PSR, 3, 1000);  // Read pressure data
        int32_t rawPressure = ((uint32_t)this->readBuffer[0] << 16) | ((uint16_t)this->readBuffer[1] << 8) | this->readBuffer[2];
        rawPressure = convert_two_complement(rawPressure, 24);  // Apply two's complement
        rawPressure /= get_scale_factor(PSR_OVERSAMPLING_RATE);  // Apply scale factor
        return rawPressure;
    }

    // Calculate the actual pressure from the raw data
    void calculate_pressure() {
        int32_t rawTemp = read_raw_temperature();  // Get raw temperature data
        int32_t rawPressure = read_raw_pressure();  // Get raw pressure data
        int32_t pressure = c00 + rawPressure * (c10 + rawPressure * (c20 + rawPressure * c30)) 
                        + rawTemp * c01 + rawTemp * rawPressure * (c11 + rawPressure * c21);  // Calculate pressure
    }

    // Override configure method from SensorBase
    void configure() override {
        read_sensor_register(DPS368_PRODUCT_ID, 1, 1000);  // Read product ID to verify sensor
        if (this->readBuffer[0] == DPS368_ID) {
            printf("DPS368 found\n");
        } else {
            printf("DPS368 not found\n");
            return;
        }

        // Wait for sensor readiness and coefficients to be ready
        while (!this->is_sensor_ready());
        while (!this->is_coef_ready());

        // Get coefficient data
        this->get_coef_source();
        this->get_coefficient();

        // Set measurement and configuration registers
        write_sensor_register(DPS368_PRS_CFG, PSR_CONFIG, 1000);
        write_sensor_register(DPS368_TMP_CFG, coef_source + TMP_CONFIG, 1000);
        this->select_mode(CON_BOTH);
    }

    // Override read method from SensorBase
    void read() override {
        // Calculate pressure and temperature
        this->calculate_pressure();
        this->calculate_temperature();
    }

    // Override generateJson method from SensorBase
    String generateJson() override {
        int32_t rawTemp = read_raw_temperature();
        int32_t rawPressure = read_raw_pressure();

        // Calculate temperature and pressure
        float temperature = c0 * 0.5f + c1 * rawTemp;
        float pressure = c00 + rawPressure * (c10 + rawPressure * (c20 + rawPressure * c30)) +
                         rawTemp * c01 + rawTemp * rawPressure * (c11 + rawPressure * c21);

        // Create the JSON string with the calculated values
        String json = "{\"sensors\":[{\"type\":\"dps368\",\"temperature\":" + String(temperature, 2) +
                      ",\"pressure\":" + String(pressure, 2) + "}]}";
        return json;
    }

    // Override send method from SensorBase
    void send() override {
        String json = generateJson();
        sendJson(sensorID, json);  // Send the JSON data over the CAN bus
    }
};
