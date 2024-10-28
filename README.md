# IoT Sensor Data Collection System

## Table of Contents
1. [Introduction](#introduction)
2. [Base Functionality](#base-functionality)
3. [Individual Subsystems](#individual-subsystems)
   - [AM2320 Temperature and Humidity Sensor](#am2320-temperature-and-humidity-sensor)
   - [TMP36 Temperature Sensor](#tmp36-temperature-sensor)
   - [Photoresistor](#photoresistor)
   - [PIR Occupancy Sensor](#pir-occupancy-sensor)
   - [Neopixel](#neopixel)
4. [Full System Integration](#full-system-integration)
5. [Calibration](#calibration)
   - [AM2320 and TMP36 Temperature](#am2320-and-tmp36-temperature)
   - [PIR Occupancy Sensor](#pir-occupancy-sensor-1)
6. [Robustness (Long-term Testing)](#robustness-long-term-testing)
7. [Productization](#productization)

## Introduction
The goal of project #1 is to produce an IoT system that collects data using sensors, and through the use of the Feather M4 and Airlift post this data to ThingSpeak. To achieve maximum functionality we plan to add four sensors collecting temperature, humidity, luminance, and occupancy data to our system. Additionally, the NeoPixel LED stick will be utilized as a status indicator for the Wi-Fi connection status and temperature calibration process. If the system cannot establish a connection to the internet, or if the temperature calibration requires new measurements, the NeoPixel will reflect this status with a red light. Conversely, if the system functions properly and posts data, the status indicators will appear green. Our system must also function autonomously for at least 48 hours and handle any exceptions and errors received.

## Base Functionality
The base functionality of our project utilizes four sensors to post data to ThingSpeak and includes a NeoPixel LED stick as a status indicator. We began by creating simple circuits that allowed us to collect data from the sensors and post it to the serial monitor to understand the wiring and code required for each sensor. After successfully creating several subsystems, we moved on to integrating the sensors into one cohesive system. Our organization kept this simple with consistent code formatting and comments, enabling us to utilize our code seamlessly in the final product. The four sensors used include the AM2320 temperature and humidity sensor, the TMP36 temperature sensor, the NSL-5152 photoresistor, and the PIR occupancy sensor.

## Individual Subsystems
Before we began, we aimed for an integrated circuit that accomplishes all desired functionality. We first needed to set up individual subsystems to get each sensor working properly. To understand how each sensor works and determine the reliability and accuracy of our measurements, we created simple circuits for each sensor. All simple subsystems were capable of posting data individually. For convenience, we developed both WiFi-accessible and offline codes, allowing us to work individually outside of the lab and the engineering IoT network. Offline versions of the code posted collected data to the serial monitor, providing insight into how to set up the sensors and simplifying the creation of a fully integrated circuit.

### AM2320 Temperature and Humidity Sensor
The AM2320 boasts long-term stability and I2C communication with temperature and humidity outputs accurate to 2-3 degrees Celsius. From the datasheet, Pin 1 is VCC, Pin 2 is Serial Data, Pin 3 is GND, and Pin 4 is Serial Clock. We determined a pull-up resistor of between 3 ohms and 10 k ohms is needed, and we used the latter. The AM2320 has a query threshold that prevents temperature and humidity from being read back-to-back. Therefore, we follow each reading and writing over I2C with a `time.sleep()`. The Feather receives the temperature and humidity as digital inputs from the AM2320 module, converting these values to Fahrenheit.

### TMP36 Temperature Sensor
To create a circuit, we first needed to find the pinout for the TMP36. According to the datasheet, the outer pins are VCC and ground, while the center pin is an analog output. The TMP36 outputs a voltage proportional to the temperature in degrees Celsius. We read the measured voltage on an analog pin and convert it to a digital value using the equation:

((pin.value * 3.3) / 65536) * 1000 which returns a measurement in mV. The equation to convert this calculated voltage to temperature is Temp in °C = [(Vout in mV) - 500] / 10. This value was also converted to Fahrenheit using the conversion (Temp°C × 9/5) + 32.

### Photoresistor
To implement the photoresistor, we used a voltage output and a voltage divider equation to determine the voltage across the photoresistor. The resistivity of the photoresistor increases when light intensity decreases, so the voltage difference measured across it provides a value proportional to light intensity. The voltage read by the Feather is sent using an analog-to-digital conversion, applying the equation:

 ((pin.value * 3.3) / 65536) * 1000
 
### PIR Occupancy Sensor
Working with the PIR occupancy sensor was the most difficult part of creating the individual subsystems. The pinout for the occupancy sensor consists of VCC and ground for the outer pins, with a digital output for the center pin. We initially connected the PIR sensor to the 3.3V power source provided by the Feather M4 but found that this was insufficient. We connected the PIR sensor to the USB connection on the Feather, which supplies 5V. The values from the PIR sensor are boolean, which we reflected as 1 or 0 per the requirements for ThingSpeak. Our final code converts these boolean values to integer values of 1 for true and 0 for false.

### Neopixel
We integrated a NeoPixel stick as a status indicator for the IoT device. The NeoPixel has four pins: VCC, Data, and two GND pins. We supplied the stick with 5V power and later dimmed the brightness to reduce stress on the circuit. The first set of two indicators displays Wi-Fi connection status, while the second set indicates if the AM2320 and TMP36 are within their margin of error. If they are not within +/- 3 degrees of each other, the IoT device will display a red indication until it successfully measures data within the error bounds and posts it.

## Full System Integration
Integrating our subsystems was seamless due to careful planning and well-documented code. We divided the work of designing the subsystems while maintaining a consistent coding style across individual files. The photoresistor is measured on analog Pin 0, the TMP36 on analog Pin 4, the PIR sensor on digital Pin 5, the NeoPixel on digital Pin 10, and the AM2320 is read over the I2C bus. There are 10 k ohm pull-up resistors on serial data and clock and a 10 k ohm pull-down resistor on analog Pin 0. When organizing our breadboard, we assigned one rail for 3.3V and one for 5V as we needed to supply two different voltages to several components. 

The final phase of our full system integration involved incorporating the Airlift to facilitate the upload of our measurements to ThingSpeak via WiFi using the ESP32. This integration process was efficient, thanks to the compatibility of the Airlift Feather Wing with the Feather M4, enabling seamless connectivity to WiFi networks. This integrated system serves as a solid foundation for continued refinement and productization.

![Integrated Circuit Drawing (Fritzing)](/images/img1.PNG)  
*Figure 1: Integrated Circuit Drawing (Fritzing)*

![Integrated Circuit Schematic (KiCAD)](/images/img2.PNG)  
*Figure 2: Integrated Circuit Schematic (KiCAD)*

## Calibration
### AM2320 and TMP36 Temperature
The AM2320 and TMP36 both measure temperature, though they excel in different aspects. The AM2320 is a more stable sensor, outputting consistent data with an accuracy of +/- 2-3 degrees Celsius. In contrast, the TMP36 is more sensitive, measuring temperature on an analog pin using voltage. Our IoT device takes five measurements using the AM2320 and averages them. This value is compared to a measurement from the TMP36 using the following function:

```python
def check_within_range(value1, value2, tolerance=3):
    return bool(abs(value1 - value2) <= tolerance)
```

If the values are within the tolerance of +/- 3 degrees Celsius, they are converted to Fahrenheit and posted to ThingSpeak along with the other data.

PIR Occupancy Sensor
The PIR Occupancy sensor was initially ineffective at detecting motion due to low sensitivity. We developed a simple code to post occupancy data every second for close monitoring:

```python
import board
import digitalio
import time
from analogio import AnalogIn

pir = digitalio.DigitalInOut(board.D5)
pir.direction = digitalio.Direction.INPUT

while True:
    print(f"Occupancy is {pir.value}")
    time.sleep(1)
```

As we monitored the data, we produced constant motion in front of the sensor, slowly increasing the sensitivity until the sensor began to read true. Our system was calibrated properly, detecting motion from both close range and distances beyond 10 feet.

## Robustness (Long-term Testing)
To ensure the robustness of our IoT sensor data collection system, we conducted long-term testing over a 48-hour period. During this time, the system was monitored for connectivity, data accuracy, and sensor reliability. The following key observations were made:

- **Connectivity:** The system maintained a stable Wi-Fi connection throughout the testing period, with only minor disruptions due to external factors.
- **Data Accuracy:** The data collected from the AM2320 and TMP36 remained consistent, with minor fluctuations within the expected error margin.
- **Sensor Reliability:** The PIR occupancy sensor proved effective at detecting motion, but we observed a need for regular adjustments in sensitivity settings based on environmental changes.

This long-term testing validated our design choices and highlighted areas for future improvement, particularly concerning sensor sensitivity and environmental adaptability.

## Productization
The final goal of our project is to productize the IoT sensor data collection system for broader applications. Potential areas for productization include:

- **Home Automation:** The system can be used in smart home applications to monitor temperature, humidity, and occupancy for energy efficiency.
- **Environmental Monitoring:** The data collected can aid in monitoring environmental conditions in urban and rural settings.
- **Security Systems:** The PIR occupancy sensor can be integrated into security systems to provide alerts based on detected motion.

![Final Design Full Assembly](/images/img4.PNG) 
*Figure 3: Final Design Full Assembly (KiCAD)*

To facilitate productization, we plan to focus on the following aspects:

1. **Compact Design:** Transitioning the breadboard prototype to a compact PCB design to enhance durability and reduce size.
2. **User Interface:** Developing a user-friendly mobile application to visualize sensor data in real-time and enable users to set parameters.
3. **Cloud Integration:** Streamlining the process for data collection and analysis through cloud platforms to enhance accessibility and usability.

In conclusion, our IoT sensor data collection system demonstrates significant potential for various applications, and with continued refinement and productization efforts, it can contribute to the growing field of smart technologies.

---

**References**
1. AM2320 Sensor Datasheet.
2. TMP36 Sensor Datasheet.
3. NSL-5152 Photoresistor Datasheet.
4. PIR Sensor Documentation.
