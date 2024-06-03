
#include <WiFi.h>
#include <DHT.h>

const char* ssid = "SLT-Fiber-2.4G";
const char* password = "0759360576";
// Timeout duration (1 minute in milliseconds)
const unsigned long timeout = 60000;
// DHT11 sensor pin
#define DHTPIN 23  // GPIO pin where the data pin is connected
// DHT sensor type
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  delay(1000);
  Serial.println("Connecting to WiFi...");

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  // Record the start time
  unsigned long startTime = millis();
  bool wifi_connected = true;
  while (WiFi.status() != WL_CONNECTED) {
    delay(2000);
    Serial.print(".");
    // Check if the timeout has been reached
    if (millis() - startTime >= timeout) {
      Serial.println("");
      Serial.println("Failed to connect to WiFi: Timeout");
      wifi_connected = false;
      break;
    }
  }
  pinMode(2, LOW);
  if(wifi_connected){
    Serial.println("");
    Serial.println("Connected to WiFi!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
  }

  // Initialize the DHT11 sensor
  dht.begin();
  
  // Read temperature and humidity values from DHT11 sensor
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  // Check if any reads failed and exit early (to try again).
  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }
  // Print the results to the Serial Monitor
  Serial.print("Humidity: ");
  Serial.print(humidity);
  Serial.print(" %\t");
  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.println(" *C");

  // Wait a few seconds between measurements
  delay(2000);
}

void loop() {
  
}
