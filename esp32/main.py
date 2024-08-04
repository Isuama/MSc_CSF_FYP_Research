#wifi
import network
from umqtt.simple import MQTTClient
#http
import urequests
#sensor
from machine import Pin
from time import sleep
import dht
import ujson
import requests
import time
# Get the current time in seconds since the epoch
import machine

# Constants - WiFi and MQTT Broker
WIFI_SSID = 'SLT-Fiber-2.4G'
WIFI_PASSWORD = '0759360576'
INFLUX_DB_IP = '192.168.1.14'
MQTT_BROKER = '192.168.1.14'
RASPBERRY_IP = '192.168.1.11'
MQTT_PORT = 1883
MQTT_TOPIC = 'w1956340/fyp_research'
MQTT_CLIENT_ID = 'esp32_client'
DHT_11_PIN = 23
# Define the parameters
bucket = "fyp_research"
start = "-1h"  # Example start time (e.g., last hour)
measurement = "esp32_measurement"
field = "secret_key"
org = "UoW"
token = "O5GiqnYRuU0sdjmAvr_1_Z-V58KA69bF-0EWqYz4HiFxGMTRkxzTHYF_MD6jOHt7WTMiBcO88v_FTjPS-nbUVA=="

def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to network...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    print('Network config:', wlan.ifconfig())

def connect_dht11(sensor):
    try:
        sleep(4)
        sensor.measure()
        temp_c = sensor.temperature()  # Temperature in Celsius
        temp_f = temp_c * (9 / 5) + 32.0  # Temperature in Fahrenheit
        # Create a dictionary with the temperature values
        data = { "Temperature_Celsius": temp_c, "Temperature_Fahrenheit": temp_f }
        # Convert to JSON string
        json_data = ujson.dumps(data)
        #print(json_data)
        return json_data  # Ensure this data is returned
    except OSError as e:
        print("Failed to read from DHT11 sensor:", e)
        return None  # Return None or an appropriate error message

def get_ecc_key():
    key = 0
    url = f"http://{RASPBERRY_IP}:5000/api/key"
    data = {'timestamp': '1234'}
    key = send_post_request(url, data)
    return key

def save_enc_stats(stats_data):
    status = "fail"
    url = f"http://{RASPBERRY_IP}:5000/api/enc_status"
    print(url)
    result = send_post_request(url, stats_data)
    print(result)

def save_ecc_key():
    status = "fail"
    url = f"http://{RASPBERRY_IP}:5000/api/status"
    # Get the current time in seconds since the epoch
    current_time_seconds = time.time()
    # Convert to milliseconds
    current_time_milliseconds = int(current_time_seconds * 1000)
    #current_time_milliseconds = time.ticks_ms()
    data = {'timestamp_in_ms': current_time_milliseconds}
    status = send_post_request_for_status(url, data)
    #print('status',status)
    return status,current_time_milliseconds

def send_post_request_for_status(url, data):
    # data should be a dictionary that will be sent as JSON
    response = urequests.post(url, json=data)
    result = response.json()
    #print('json:',result)
    status = response.json().get("status", None)  # Get the value associated with the key
    return status

def send_post_request(url, data):
    # data should be a dictionary that will be sent as JSON
    response = urequests.post(url, json=data)
    result = response.json()
    #print('json:',result)
    key = response.json().get("key", None)  # Get the value associated with the key
    return key

def xor_encrypt(message, key):
    encrypted = ''.join(chr(ord(char) ^ key) for char in message)
    return encrypted

def encrypt_message(message,key):
    encrypted_message = xor_encrypt(message, key)
    #print("Encrypted:", encrypted_message)
    return encrypted_message;

def decrypt_message(encrypted_message,key):
    decrypted_message = xor_encrypt(encrypted_message, key)
    print("Decrypted:", decrypted_message)
    return decrypted_message;

def mqtt_publish(message):
    # Set up MQTT client and connect
    client = setup_mqtt_client(MQTT_BROKER, MQTT_CLIENT_ID)
    #print('successfully connected to mqtt')
    client.publish(MQTT_TOPIC, message)
    #print(f"Message '{message}' published to topic '{MQTT_TOPIC}'")
    # Disconnect MQTT
    client.disconnect()

def setup_mqtt_client(server, client_id):
    client = MQTTClient(client_id, server, port=MQTT_PORT)
    client.connect()
    #print(f"Connected to MQTT Broker on {server}")
    return client

def read_influxdb_from_timestamp(timestamp_in_ms):
    # Construct the Flux query
    flux_query = f'''
    from(bucket: "{bucket}")
    |> range(start: {start})
    |> filter(fn: (r) => r._measurement == "{measurement}")
    |> filter(fn: (r) => r.timestamp_in_ms == "{timestamp_in_ms}")
    |> filter(fn: (r) => r._field == "{field}")
    '''

    # Construct the full URL for the HTTP POST request
    url = f"http://{INFLUX_DB_IP}:8086/api/v2/query?org={org}"
    print(url)
    # Construct the request payload
    data = {
        "query": flux_query,
        "type": "flux"
    }

    # Set up the headers (assuming you need a token for authentication)
    headers = {
        "Authorization": f"Token {token}",
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
                #print(f"Secret Key Value: {secret_key_value}")
                return secret_key_value
            else:
                print("Error: The line does not have enough values.")
        else:
            print("Error: The response does not have enough lines.")
    else:
        print(f"Error: {response.status_code}, {response.text}")

# current memory usage in MB
def get_memory_usage():
    gc.collect()
    total_memory = gc.mem_alloc() + gc.mem_free()
    free_memory = gc.mem_free()
    used_memory = gc.mem_alloc()
    return total_memory, free_memory, used_memory


# Main function to connect to WiFi and MQTT, then publish a message
def main():
    
    # Connect to WiFi
    connect_wifi(WIFI_SSID, WIFI_PASSWORD)
    
    #connect_to_dht11
    sensor = dht.DHT11(Pin(DHT_11_PIN))
    while True:
        
        # utilization calculation starts
        total_memory, free_memory, used_memory = get_memory_usage()
        start = time.ticks_us()
        gc.collect()  # Run garbage collector to get an accurate measure
        total_memory = gc.mem_alloc() + gc.mem_free()  # Total memory in bytes
        memory_before = gc.mem_free()
        #cpu
        cpu_freq = machine.freq()  # Get the CPU frequency in Hz
        start_time = time.ticks_us()
        
        json_result = connect_dht11(sensor)
        print('raw data',json_result)
        #encrypt record
        #step 1 - get the key
        #key = int(get_ecc_key())
        
        #ask to generate ecc key
        status,current_time_milliseconds = save_ecc_key()
        #print('status received:',status)
        if status == "success":
            # read from influxdb
            key = read_influxdb_from_timestamp(current_time_milliseconds)
        else:
            print('error on retreiving key')
            break
            
        #key = 146
        if key==0:
            print('erro on receiving encryption key')
            break
        #step 2 - encrypt the message using the key
        #encrypt
        #print('going to encrypt the message:',json_result,key)
        encrypted_message = encrypt_message(json_result,int(key))
        print('encrypted message is:',encrypted_message)        
        #decrypt
        #decrypt_message(encrypted_message,key)
        #-----full_msg = encrypted_message+str(current_time_milliseconds)
        #print('full msg:',full_msg[:-12])
        #nw_msg = full_msg[:-12]
        #print('new message:',nw_msg)
        #nw_key = read_influxdb_from_timestamp(str(full_msg[-12:]))
        #print('new msg:',nw_msg)
        #print('new key:',nw_key)
        #print(decrypt_message(nw_msg,int(nw_key)))
            
        # Publish encrypted message
        #mqtt_message = json_result
        mqtt_message = encrypted_message+str(current_time_milliseconds)
        #mqtt_message = {"msg":encrypted_message, "timestamp":current_time_milliseconds}
        #going to base64 encode
        message_bytes = mqtt_message.encode('utf-8')
        mqtt_message = message_bytes
        
        #print('going to publish to mqtt:',mqtt_message)
        mqtt_publish(mqtt_message)
        
        #utilization calculation
        end = time.ticks_us()
        task_duration_us = time.ticks_diff(end, start)
        start_period = time.ticks_us()
        time.sleep(1)
        end_period = time.ticks_us()
        period_duration_us = time.ticks_diff(end_period, start_period)
        cpu_usage_percentage = (task_duration_us / period_duration_us) 
        mem_usage_percentage = (used_memory/total_memory) * 100
        #cpu_freq = machine.freq()
        system_stats = { "cpu_freq": cpu_freq, "cpu_usage_percentage": cpu_usage_percentage,"task_duration": task_duration_us,
        "total_memory": total_memory,"free_memory": free_memory,"used_memory": used_memory,"memory_usage_percentage":mem_usage_percentage}
        print("System Statistics:", system_stats)
        save_enc_stats(system_stats)
        
if __name__ == "__main__":
    main()

