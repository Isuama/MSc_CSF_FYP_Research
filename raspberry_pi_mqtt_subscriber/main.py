import paho.mqtt.client as mqtt
import requests
import psutil
import influxdb_client
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import time

# Constants - InfluxDB
INFLUX_URL = "http://192.168.1.14:8086/"
BUCKET = "fyp_research"
START = "-1h"
MEASUREMENT = "esp32_measurement"
FIELD = "secret_key"
ORG = "UoW"
TOKEN = "9UebI5yEvAYTM-AjI6LGVvsgfa3k_SllX_4K9AB9Y9zvQWHLIJniI5-zfvu8v0SVU8pHK-ZejBMmAunAn-jBNA=="

# Constant - MQTT
MQTT_BROKER = "192.168.1.14"
MQTT_PORT = 1883
MQTT_TOPIC = "w1956340/fyp_research"

#decryption stats - influx db
DEC_MEM_MEASUREMENT = "memory"
DEC_CPU_MEASUREMENT = "cpu"
DEC_TASK_MEASUREMENT = "task"
STATS_BUCKET = "fyp_stats"

def get_cpu_info():
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_cores = psutil.cpu_count(logical=False)
    cpu_threads = psutil.cpu_count(logical=True)
    return {
        "cpu_percent": cpu_percent,
        "cpu_cores": cpu_cores,
        "cpu_threads": cpu_threads
    }

def get_memory_info():
    virtual_mem = psutil.virtual_memory()
    swap_mem = psutil.swap_memory()
    return {
        "total_memory": virtual_mem.total,
        "available_memory": virtual_mem.available,
        "used_memory": virtual_mem.used,
        "memory_percent": virtual_mem.percent,
        "total_swap": swap_mem.total,
        "used_swap": swap_mem.used,
        "swap_percent": swap_mem.percent
    }


# Define callback functions for MQTT events
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribe to the topic for new messages
    client.subscribe(MQTT_TOPIC)


def write_measurement(execution_time):
    try:        
        # write stats to influx db
        client = InfluxDBClient(url=INFLUX_URL, token=TOKEN, org=ORG)
        write_api = client.write_api(write_options=SYNCHRONOUS)

        # cpu measurement -raspberry pi
        cpu_info = get_cpu_info()
        
        cpu_percent = cpu_info['cpu_percent']
        cpu_percent_record = influxdb_client.Point(DEC_CPU_MEASUREMENT).tag("device","raspberry").tag("type","cpu_percent").field("cpu_percent", cpu_percent)
        write_api.write(bucket=STATS_BUCKET, org=ORG, record=cpu_percent_record)

        cpu_cores = cpu_info['cpu_cores']
        cpu_cores_record = influxdb_client.Point(DEC_CPU_MEASUREMENT).tag("device","raspberry").tag("type","cpu_cores").field("cpu_cores", cpu_cores)
        write_api.write(bucket=STATS_BUCKET, org=ORG, record=cpu_cores_record)

        cpu_threads = cpu_info['cpu_threads']
        cpu_threads_record = influxdb_client.Point(DEC_CPU_MEASUREMENT).tag("device","raspberry").tag("type","cpu_threads").field("cpu_threads", cpu_threads)
        write_api.write(bucket=STATS_BUCKET, org=ORG, record=cpu_threads_record)
    
        # memory measurement -raspberry pi
        memory_info = get_memory_info()

        total_memory = memory_info['total_memory']
        total_memory_record = influxdb_client.Point(DEC_MEM_MEASUREMENT).tag("device","raspberry").tag("type","total_memory").field("total_memory", total_memory)
        write_api.write(bucket=STATS_BUCKET, org=ORG, record=total_memory_record)

        available_memory = memory_info['available_memory']
        available_memory_record = influxdb_client.Point(DEC_MEM_MEASUREMENT).tag("device","raspberry").tag("type","available_memory").field("available_memory", available_memory)
        write_api.write(bucket=STATS_BUCKET, org=ORG, record=available_memory_record)

        used_memory = memory_info['used_memory']
        used_memory_record = influxdb_client.Point(DEC_MEM_MEASUREMENT).tag("device","raspberry").tag("type","used_memory").field("used_memory", used_memory)
        write_api.write(bucket=STATS_BUCKET, org=ORG, record=used_memory_record)

        memory_percent = memory_info['memory_percent']
        memory_percent_record = influxdb_client.Point(DEC_MEM_MEASUREMENT).tag("device","raspberry").tag("type","memory_percent").field("memory_percent", memory_percent)
        write_api.write(bucket=STATS_BUCKET, org=ORG, record=memory_percent_record)

        total_swap = memory_info['total_swap']
        total_swap_record = influxdb_client.Point(DEC_MEM_MEASUREMENT).tag("device","raspberry").tag("type","total_swap").field("total_swap", total_swap)
        write_api.write(bucket=STATS_BUCKET, org=ORG, record=total_swap_record)

        used_swap = memory_info['used_swap']
        used_swap_record = influxdb_client.Point(DEC_MEM_MEASUREMENT).tag("device","raspberry").tag("type","used_swap").field("used_swap", used_swap)
        write_api.write(bucket=STATS_BUCKET, org=ORG, record=used_swap_record)

        swap_percent = memory_info['swap_percent']
        swap_percent_record = influxdb_client.Point(DEC_MEM_MEASUREMENT).tag("device","raspberry").tag("type","swap_percent").field("swap_percent", swap_percent)
        write_api.write(bucket=STATS_BUCKET, org=ORG, record=swap_percent_record)

        decryption_time_record = influxdb_client.Point(DEC_TASK_MEASUREMENT).tag("device","raspberry").tag("type","decryption_time").field("decryption_time", execution_time)
        write_api.write(bucket=STATS_BUCKET, org=ORG, record=decryption_time_record)

        """
        print("\nMemory Information:")
        print(f"Total Memory: {memory_info['total_memory'] / (1024**2):.2f} MB")
        print(f"Available Memory: {memory_info['available_memory'] / (1024**2):.2f} MB")
        print(f"Used Memory: {memory_info['used_memory'] / (1024**2):.2f} MB")
        print(f"Memory Usage: {memory_info['memory_percent']}%")
        print(f"Total Swap: {memory_info['total_swap'] / (1024**2):.2f} MB")
        print(f"Used Swap: {memory_info['used_swap'] / (1024**2):.2f} MB")
        print(f"Swap Usage: {memory_info['swap_percent']}%")
        """
        print("measurement successfully written")
    except Exception as e:
        print(f"An error occurred on the subscribed message: {e}")

def on_message(client, userdata, received_message):
    try:
        start_time = time.time()
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
        end_time = time.time()
        execution_time = end_time - start_time
        write_measurement(execution_time)

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
        url = INFLUX_URL + f"api/v2/query?org={ORG}"

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