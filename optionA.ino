#include <WiFi.h>
#include <ESPAsyncWebServer.h>
#include <ArduinoJson.h>

// 1. Network Settings
const char* ssid = "EMG_Monitor_Pro";
const char* password = "password123";

// 2. Hardware Settings
const int EMG_PIN = 34; // GPIO 34 (Analog In)

// 3. Create Server & WebSocket
AsyncWebServer server(80);
AsyncWebSocket ws("/ws");

unsigned long lastTime = 0;
const int timerDelay = 20; // 20ms = 50Hz

void onEvent(AsyncWebSocket *server, AsyncWebSocketClient *client, AwsEventType type,
             void *arg, uint8_t *data, size_t len) {
  if (type == WS_EVT_CONNECT) {
    Serial.printf("Client #%u connected\n", client->id());
  } else if (type == WS_EVT_DISCONNECT) {
    Serial.printf("Client #%u disconnected\n", client->id());
  }
}

void setup() {
  Serial.begin(115200);

  // Start Access Point
  WiFi.softAP(ssid, password);
  Serial.println("--- Wi-Fi Started ---");
  Serial.print("Connect to: "); Serial.println(ssid);
  Serial.print("ESP32 IP: "); Serial.println(WiFi.softAPIP());

  // Attach WebSocket to Server
  ws.onEvent(onEvent);
  server.addHandler(&ws);

  // Start Server
  server.begin();
}

void loop() {
  ws.cleanupClients(); // Keep memory clean

  if (millis() - lastTime > timerDelay) {
    int rawValue = analogRead(EMG_PIN);

    // Create a small, fast JSON packet
    StaticJsonDocument<64> doc;
    doc["v"] = rawValue; // 'v' for value
    doc["t"] = millis(); // 't' for time

    String msg;
    serializeJson(doc, msg);
    
    // Send to all connected browsers
    ws.textAll(msg);
    
    lastTime = millis();
  }
}