# wifi-packages
import network
from umqtt.simple import MQTTClient
# http-packages
import urequests
# sensor-packages
from machine import Pin
from time import sleep
import dht
import ujson
import requests

# Constants - WiFi
WIFI_SSID = 'SLT-Fiber-2.4G'
WIFI_PASSWORD = '0759360576'

# Constants - ECC Key genertation
ECC_BASE_ENDPOINT = "http://192.168.1.13:5000/"

# Constants - MQTT
MQTT_BROKER = '192.168.1.11'
MQTT_PORT = 1883
MQTT_TOPIC = 'w1956340/fyp_research'
MQTT_CLIENT_ID = 'esp32_client'

# Constants - Sensors
DHT_11_PIN = 23
DHT_11_SLEEP_TIME = 3# collect data on every 4 seconds

# Constant -  InfluxDB
INFLUX_ENDPOINT = "http://192.168.1.11:8086/"
BUCKET = "fyp_research"
START = "-1h" 
MEASUREMENT = "esp32_measurement"
FIELD = "secret_key"
ORG = "UoW"
TOKEN = "9UebI5yEvAYTM-AjI6LGVvsgfa3k_SllX_4K9AB9Y9zvQWHLIJniI5-zfvu8v0SVU8pHK-ZejBMmAunAn-jBNA=="

# Connect Wi-Fi
def connect_wifi(ssid, password):
    try:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        if not wlan.isconnected():
            print('Connecting to network...')
            wlan.connect(ssid, password)
            while not wlan.isconnected():
                pass
        # Print network configuration on a successfull connection
        print('Successfully Connected to the Network. Network config:', wlan.ifconfig())
    except Exception as e:
        print("Failed to connect to the Wi-Fi:", e)
        return None

def connect_dht11(sensor):
    try:
        # collect record on every 4 seconds, this is customizable.
        sleep(DHT_11_SLEEP_TIME)
        sensor.measure()
        temp_c = sensor.temperature()  # Temperature in Celsius
        temp_f = temp_c * (9 / 5) + 32.0  # Temperature in Fahrenheit
        # Create a dictionary with the temperature values
        data = { "Temperature_Celsius": temp_c, "Temperature_Fahrenheit": temp_f }
        # Convert collected data to a JSON string
        json_data = ujson.dumps(data)
        return json_data  # return collected raw data
    except Exception as e:
        print("Failed to read from DHT11 sensor:", e)
        return None

def generate_ecc_key():
    try:
        # Set the initial status to the fail
        status = "fail"
        # set URL to get the ecc key geenration status
        url = ECC_BASE_ENDPOINT + 'api/status'
        # Get the current time in seconds
        current_time_seconds = time.time()
        # Convert to milliseconds
        current_time_milliseconds = int(current_time_seconds * 1000)
        data = {'timestamp_in_ms': current_time_milliseconds}
        # Send POST request to get the ecc key status
        status = send_post_request_for_status(url, data)
        #print("ECC key geenration status and timestamp", status, current_time_milliseconds)
        return status,current_time_milliseconds
    except Exception as e:
        print("Exception occuered while generating ECC key:", e)
        return None

def send_post_request_for_status(url, data):
    try:
        # send data in a json format and convert the result to json
        response = urequests.post(url, json=data).json()
        # print("sending post request success: ", response)
        status = response.get("status", None)  # Get the value associated with the key
        return status
    except Exception as e:
        print("Exception occuered while sending POST request to get the ECC key geenration status:", e)
        return None

def get_key_from_influxdb(timestamp_in_ms):
    try:
        # Construct the Flux query
        flux_query = f'''
        from(bucket: "{BUCKET}")
        |> range(start: {START})
        |> filter(fn: (r) => r._measurement == "{MEASUREMENT}")
        |> filter(fn: (r) => r.timestamp_in_ms == "{timestamp_in_ms}")
        |> filter(fn: (r) => r._field == "{FIELD}")
        '''

        # Construct the full URL for the HTTP POST request
        url = INFLUX_ENDPOINT + f"api/v2/query?org={ORG}"

        # Construct the request payload
        data = {
            "query": flux_query,
            "type": "flux"
        }

        # Set up the headers with the pre-generated token
        headers = {
            "Authorization": f"Token {TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/csv"
        }

        # Send the POST request
        response = requests.post(url, headers=headers, json=data)

        # Check the response status code and print the result
        if response.status_code == 200:
            # Split the response by lines
            lines = response.text.splitlines()
    
            if len(lines) > 1:
                # Split the second line by commas to get the values
                values = lines[1].split(',')
        
                if len(values) >= 8:
                    secret_key_value = values[6]
                    return secret_key_value
                else:
                    print("Error: The line does not have enough values.")
            else:
                print("Error: The response does not have enough lines.")
        else:
            print(f"Error: {response.status_code}, {response.text}")
    except Exception as e:
        print("Exception occuered while retreiving key from InfluxDB:", e)
        return None

def encrypt_message(message,key):
    try:
        # encrypt message with XOR mechanism
        encrypted_message = xor_encrypt(message, key)
        return encrypted_message
    except Exception as e:
        print("Exception occuered while encrypting the message with the received key:", e)
        return None

def xor_encrypt(message, key):
    try:
        encrypted = ''.join(chr(ord(char) ^ key) for char in message)
        return encrypted
    except Exception as e:
        print("Exception occuered while encrypting the message in xor mechanism:", e)
        return None

def decrypt_message(encrypted_message,key):
    try:
        decrypted_message = xor_encrypt(encrypted_message, key)
        return decrypted_message
    except Exception as e:
        print("Exception occuered while decrypting the message in xor mechanism:", e)
        return None

def mqtt_publish(message):
    try:
        # Set up MQTT client and connect
        client = setup_mqtt_client(MQTT_BROKER, MQTT_CLIENT_ID)
        #print('successfully connected to mqtt')
        client.publish(MQTT_TOPIC, message)
        print(f"Message '{message}' published to topic '{MQTT_TOPIC}'")
        # Disconnect MQTT
        client.disconnect()
    except Exception as e:
        print("Exception occuered while publishing message to the MQTT client", e)
        return None

def setup_mqtt_client(server, client_id):
    try:
        client = MQTTClient(client_id, server, port=MQTT_PORT)
        client.connect()
        print(f"Connected to MQTT Broker on {server}")
        return client
    except Exception as e:
        print("Exception occuered while connecting to the mqtt client:", e)
        return None

# Main function
def main():
    try:
        # Connect to WiFi
        connect_wifi(WIFI_SSID, WIFI_PASSWORD)
    
        # Connect to DHT-11 sensor
        sensor = dht.DHT11(Pin(DHT_11_PIN))
        while True:
            json_result = connect_dht11(sensor)
            print("Raw data collected: ",json_result)
            
            # Raw data encryption starts
            # STEP-01 - generate the key and save in influxdb - execute outside function to generate ecc-key for a given timestamp
            status,current_time_milliseconds = generate_ecc_key()
            if status == 	"success": # success means, key is generated and succefully added to the influx db
                # retreive the key from influxdb for the given timestamp
                key = get_key_from_influxdb(current_time_milliseconds)
                # print("key is collected: ",key)
            else:
                print("error on retreiving key")
                break

            if isinstance(key, (int, float)) and key > 0: # key should always be  a number and greater than 0, otherwise it is considered as an invalid key
                print('erro on receiving encryption key')
                break

            # STEP-02 - encrypt the message using the generated key
            encrypted_message = encrypt_message(json_result,int(key))
            print("Raw data encrypted successfully. : ", encrypted_message)

            # Decrypt the message - This is not executed in the ESP32, but for the testing purposes
            # append timestamp to the encrypted message
            encrypted_message_with_timestamp = encrypted_message+str(current_time_milliseconds)
            print("encrypted message append with the timestamp: ", encrypted_message_with_timestamp)
            # Extract timestamp and encrypted message for the decryption process
            extracted_encrypted_message = encrypted_message_with_timestamp[:-12]
            extracted_timestamp = get_key_from_influxdb(str(encrypted_message_with_timestamp[-12:]))
            #print("Extracted encrypted message: ",extracted_encrypted_message)
            #print("Extracted timestamp: ",extracted_timestamp)
            #print("Decrypted message: ",decrypt_message(extracted_encrypted_message,int(extracted_timestamp)))
            
            # Publish encrypted message with the timestamp attached to it
            # encode message prior transmitting to achieve the accuracy
            encoded_message = encrypted_message_with_timestamp.encode('utf-8')
            print("encode message to publish via mqtt: ", encoded_message)
            # publish encoded message via mqtt
            mqtt_publish(encoded_message)
    except Exception as e:
        print("Exception occurred in the main functionalities:", e)
        return None

if __name__ == "__main__":
    main()