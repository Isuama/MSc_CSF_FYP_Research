import paho.mqtt.client as mqtt
import requests

# Constants - InfluxDB
INFLUX_ENDPOINT = "http://192.168.1.2:8086/"
BUCKET = "fyp_research"
START = "-1h"
MEASUREMENT = "esp32_measurement"
FIELD = "secret_key"
ORG = "UoW"
TOKEN = "9UebI5yEvAYTM-AjI6LGVvsgfa3k_SllX_4K9AB9Y9zvQWHLIJniI5-zfvu8v0SVU8pHK-ZejBMmAunAn-jBNA=="

# Constant - MQTT
MQTT_BROKER = "192.168.1.2"
MQTT_PORT = 1883
MQTT_TOPIC = "w1956340/fyp_research"

# Define callback functions for MQTT events
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribe to the topic for new messages
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, received_message):
    try:
        # decode message
        decoded_msg = received_message.payload.decode('utf-8')
    
        # extract encrypted message
        extracted_encrypted_message = decoded_msg[:-12]
        print("received encrypted message:", extracted_encrypted_message)
    
        # extract timestamp
        extracted_timestamp = decoded_msg[-12:]
        # retreieve key from the influx db based on the extracted timestamp
        decryption_key = get_key_from_influxdb(str(extracted_timestamp))
        
        # Decrypt message
        print("Decryptd message: ",decrypt_message(extracted_encrypted_message,int(decryption_key)))
    except Exception as e:
        print(f"An error occurred on the subscribed message: {e}")


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

def decrypt_message(message,key):
    try:
        # encrypt message with XOR mechanism
        encrypted_message = xor_decrypt(message, key)
        return encrypted_message
    except Exception as e:
        print("Exception occuered while encrypting the message with the received key:", e)
        return None

def xor_decrypt(message, key):
    try:
        encrypted = ''.join(chr(ord(char) ^ key) for char in message)
        return encrypted
    except Exception as e:
        print("Exception occuered while encrypting the message in xor mechanism:", e)
        return None

# Create a MQTT client instance
client = mqtt.Client()

# Set callback functions
client.on_connect = on_connect
client.on_message = on_message

# Connect to MQTT broker
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Start the MQTT loop
client.loop_forever()