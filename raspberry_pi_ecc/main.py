from flask import Flask, request, jsonify
import influxdb_client
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from tinyec import registry
import secrets
import time
import psutil

# Constants - InfluxDB
INFLUX_URL = "http://192.168.1.14:8086"
BUCKET = "fyp_research"
START = "-1h"
MEASUREMENT = "esp32_measurement"
FIELD = "secret_key"
ORG = "UoW"
TOKEN = "9UebI5yEvAYTM-AjI6LGVvsgfa3k_SllX_4K9AB9Y9zvQWHLIJniI5-zfvu8v0SVU8pHK-ZejBMmAunAn-jBNA=="

#encryption stats - influx db
ENC_MEM_MEASUREMENT = "memory"
ENC_CPU_MEASUREMENT = "cpu"
ENC_TASK_MEASUREMENT = "task"

def create_key_pair(curve_name):
  try:
    curve = registry.get_curve(curve_name)
    private_key = secrets.randbelow(curve.field.n)
    public_key = private_key * curve.g
    return private_key, public_key
  except Exception as e:
    print(f"An error occurred while generating key pair: {e}")

def get_ecc_encryption_key():
  try:
    curve_name = "brainpoolP256r1"
    primary_private,primary_public = create_key_pair(curve_name)
    secondary_private,secondary_public = create_key_pair(curve_name)
    primary_secret = primary_private * secondary_public
    secondary_secret = secondary_private * primary_public
    return primary_secret
  except Exception as e:
    print(f"An error occurred while generating ecc key: {e}")

def write_encryption_stats(data):
  try:
    client = InfluxDBClient(url=INFLUX_URL, token=TOKEN, org=ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)
    total_memory = data.get('total_memory')
    free_memory = data.get('free_memory')
    used_memory = data.get('used_memory')
    memory_usage_percentage = data.get('memory_usage_percentage')
    print(total_memory,free_memory,used_memory,memory_usage_percentage)

    # memory measurement
    total_memory = influxdb_client.Point(ENC_MEM_MEASUREMENT).tag("device","esp-32").tag("type","total_memory").field("total_memory", total_memory)
    write_api.write(bucket="fyp_stats", org=ORG, record=total_memory)
    
    free_memory = influxdb_client.Point(ENC_MEM_MEASUREMENT).tag("device","esp-32").tag("type","free_memory").field("free_memory", free_memory)
    write_api.write(bucket="fyp_stats", org=ORG, record=free_memory)
    
    used_memory = influxdb_client.Point(ENC_MEM_MEASUREMENT).tag("device","esp-32").tag("type","used_memory").field("used_memory", used_memory)
    write_api.write(bucket="fyp_stats", org=ORG, record=used_memory)
    
    memory_usage_percentage = influxdb_client.Point(ENC_MEM_MEASUREMENT).tag("device","esp-32").tag("type","memory_usage_percentage").field("memory_usage_percentage", memory_usage_percentage)
    write_api.write(bucket="fyp_stats", org=ORG, record=memory_usage_percentage)

    #cpu measurement
    cpu_freq = influxdb_client.Point(ENC_CPU_MEASUREMENT).tag("device","esp-32").tag("type","cpu_freq").field("cpu_freq", cpu_freq)
    write_api.write(bucket="fyp_stats", org=ORG, record=cpu_freq)

    cpu_usage_percentage = influxdb_client.Point(ENC_CPU_MEASUREMENT).tag("device","esp-32").tag("type","cpu_usage_percentage").field("cpu_usage_percentage", cpu_usage_percentage)
    write_api.write(bucket="fyp_stats", org=ORG, record=cpu_usage_percentage)



    print('stats data successfully added to the influxdb:')
    return True
  except Exception as e:
    print(f"An error occurred while writing stats data: {e}")
    return False
  finally:
    client.close()
def write_data(timestamp_in_ms,secret_key):
  try:
    # Create a client object
    client = InfluxDBClient(url=INFLUX_URL, token=TOKEN, org=ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)
    p = influxdb_client.Point(MEASUREMENT).tag("timestamp_in_ms", timestamp_in_ms).field("secret_key", secret_key)
    write_api.write(bucket=BUCKET, org=ORG, record=p)
    print('data successfully added to the influxdb:',timestamp_in_ms,secret_key)
  except Exception as e:
    print(f"An error occurred while writing data: {e}")
  finally:
    client.close()

def get_key_influxdb(timestamp_in_ms):
    query_template = '''
    from(bucket:"{bucket}")
    |> range(start: {start})
    |> filter(fn:(r) => r._measurement == "{measurement}")
    |> filter(fn:(r) => r.timestamp_in_ms == "{timestamp_in_ms}")
    |> filter(fn:(r) => r._field == "{field}")'''

    # Define parameters
    parameters = {
        "bucket": BUCKET,
        "start": START,
        "measurement": MEASUREMENT,
        "timestamp_in_ms": timestamp_in_ms,
        "field": "secret_key"
    }
    try:
        client = InfluxDBClient(url=INFLUX_URL, token=TOKEN, org=ORG)
        query = query_template.format(**parameters)
        result = client.query_api().query(query, org=ORG)
        results = []
        for table in result:
            for record in table.records:
                results.append((record.get_field(), record.get_value()))
            return results[0]

    except Exception as e:
        print(f"An error occurred while retrieving data: {e}")
    finally:
      client.close()

app = Flask(__name__)
@app.route('/api/enc_status',methods=['POST'])
def api_enc_status_data():
  try:
    data = request.get_json()
    if(write_encryption_stats(data)):
      data = {'status': "success"}
    else:
      data = {'status': "fail"}
    return jsonify(data)
  except Exception as e:
    print(f"An error occurred in API get key: {e}")

@app.route('/api/status',methods=['POST'])
def api_status_data():
  try:
    data = request.get_json()
    # Extract timestamp from JSON data
    timestamp_in_ms = data.get('timestamp_in_ms')
    secret = get_ecc_encryption_key()
    secret_key = secret.x % 256
    write_data(timestamp_in_ms,secret_key)
    if(secret_key>0):
      data = {'status': "success"}
    else:
      data = {'status': "fail"}
    return jsonify(data)
  except Exception as e:
    print(f"An error occurred in API get key: {e}")

@app.route('/api/key',methods=['POST'])
def api_write_data():
  try:
    data = request.get_json()
    # Extract timestamp from JSON data
    timestamp_in_ms = data.get('timestamp_in_ms')
    secret = get_ecc_encryption_key()
    secret_key = secret.x % 256
    write_data(timestamp_in_ms,secret_key)
    data = {'key': secret_key}
    return jsonify(data)
  except Exception as e:
    print(f"An error occurred in API get key: {e}")

@app.route('/api/secret',methods=['GET'])
def api_read_data():
  try:
    data = request.get_json()
    timestamp_in_ms = data.get('timestamp_in_ms')
    secret_key = get_key_influxdb(timestamp_in_ms)
    data = {'key': secret_key}
    return jsonify(data)
  except Exception as e:
    print(f"An error occurred while retrieving they key from timestamp: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)