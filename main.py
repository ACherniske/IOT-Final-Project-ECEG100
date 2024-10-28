import time
import board
import busio
import adafruit_am2320
import digitalio
from digitalio import DigitalInOut
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager
from analogio import AnalogIn

# Choose "home" or "Bucknell"
location = "Bucknell"

# Get wifi details and more from a secrets.py file
# Determine if the location is home or Bucknell
if location == "home":
    try:
        from secrets import secrets_home
    except ImportError:
        print("WiFi secrets are kept in secrets.py, please add them there!")
        raise
    secrets = secrets_home
else:
    try:
        from secrets import secrets_Bucknell
    except ImportError:
        print("WiFi secrets are kept in secrets.py, please add them there!")
        raise
    secrets = secrets_Bucknell

# For the AirLift Featherwing:
esp32_cs = DigitalInOut(board.D13)
esp32_ready = DigitalInOut(board.D11)
esp32_reset = DigitalInOut(board.D12)

spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets, status_pixel=None)

if esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
    print("ESP32 found and in idle mode")
print("Firmware vers.", esp.firmware_version)
print("MAC addr:", [hex(i) for i in esp.MAC_address])

print("Connecting to AP...")
while not esp.is_connected:
    try:
        esp.connect_AP(secrets["ssid"], secrets["password"])
    except Exception as e:
        print("could not connect to AP, retrying: ", e)
        continue
print("Connected to", str(esp.ssid, "utf-8"), "\tRSSI:", esp.rssi)
print("My IP address is", esp.pretty_ip(esp.ip_address))

Analog_In = AnalogIn(board.A0)


def get_voltage(pin):
    return ((pin.value * 3.3) / 65536) * 1000


Analog_In2 = AnalogIn(board.A4)


def get_tempTMP(pin):
    # we want to convert our analog input to a voltage in millivolts for calculations
    voltage = (pin.value * 3300) / 65536
    # Equation given by adafruit for converting voltage to temperature
    tempc = (voltage - 500) / 10
    # Converting temperature in Celsius to degrees Fahrenheit
    return (tempc * (9 / 5)) + 32

#To set up the I2C path for the AM2320 sensor
i2c = board.I2C()
sensor = adafruit_am2320.AM2320(i2c)

# Define your ThingSpeak Write API Key in your secrets.py file with key 'Write_API_Key'
# This loop will run continuously and reset the Wifi connection if the post fails

# To import the API key from the secrets file
from secrets import Write_API_Key

while True:
    # Define the string s to contain the HTTP API request to post sensor data to ThingSpeak.
    # Your api_key is in secrets['Write_API_Key'] if you define it in the secrets.py file.

    # To take the measurements for voltage of photoresistor and TMP36 sensor
    currentPRvoltage = get_voltage(Analog_In)
    currentTMPtemp = get_tempTMP(Analog_In2)
    
    #Since the temperature must be converted to Fahrenheit
    currentAM2320temp = (float(sensor.temperature) * (9/5)) + 32
    #An error arises if there is not any time between temperature and humidity readings on the AM2320 sensor
    time.sleep(1)
    currentAM2320humid = sensor.relative_humidity

    #To take an occupancy measurement and report True with a value of 1 and False with a value of 0
    if pir.value == True:
        CurrentOcc = 1
    elif pir.value == False:
        CurrentOcc = 0

    # Modified f string to contain API key and measured current temperature and voltage
    s = f"https://api.thingspeak.com/update?api_key={Write_API_Key}&field1={currentPRvoltage}&field2={currentTMPtemp}&field3={currentAM2320temp}&field4={currentAM2320humid}&field5={CurrentOcc}"

    try:
        response = wifi.post(s)
        print("Data posted with index number:")
        print(response.text)
        print(f"Temperature from TMP36 was measured as {currentTMPtemp} deg F and photoresistor voltage was measured as {currentPRvoltage} mV. AM2320 sensor measured temperature as {currentAM2320temp} deg f")
        response.close()
    except RuntimeError as e:
        print("Failed to post data, retrying\n", e)
        wifi.reset()
        continue
    # Add code here to sleep until the next measurement
    time.sleep(300)
