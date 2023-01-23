# Wind Module
This directory contains the scripts to collect wind speed and direction data from the anemometer, and publishes these data to the MQTT broker.

- [Wind Module](#wind-module)
  - [Basic Setup and Usage](#basic-setup-and-usage)
  - [Testing](#testing)

<br>

## Basic Setup and Usage
1. Install the [Vaisala USB Instrument Finder driver](https://go.vaisala.com/software/WXT530/Vaisala_WXT530_Configuration_Tool_Weather_Measurement.zip?_ga=2.138439603.1803271655.1674458831-1555859295.1674458831) using these [installation instructions](https://docs.vaisala.com/r/M211840EN-F/en-US/GUID-6D206CCD-21E9-4E9A-98C9-760C90EA90BF/GUID-AE6CDFA9-16A5-4E47-B354-37C04534C558).

2. Connect the anemometer to you computer and note down which port it is connecting to.

3. In the `wind_module` directory, create a local version of `config.py` using the `config.example.py` file. 

4. Get inside the `wind_module_directory` using:
     ```
     cd wireless_mdoules_py/wind_module
    ```

5. Ensure that you have [poetry](https://python-poetry.org/) installed, spawn into the poetry environment using:
    ```
    poetry shell
    ```

6. Run the main program using:
    ```
    python main.py
    ```

After completing these steps, the anemometer should be collecting wind speed and direction data, and publishing these data to the MQTT broker under the topic `/v3/wireless_module/5/data`.

<br>
