/*
   reference: 
   
   https://docs.labs.mediatek.com/resource/linkit7697-arduino/zh_tw/developer-guide/using-the-wi-fi-library
   https://blog.gtwang.org/iot/raspberry-pi/raspberry-pi-mosquitto-mqtt-broker-iot-integration/
   https://randomnerdtutorials.com/why-you-shouldnt-always-use-the-arduino-delay-function/
   https://swf.com.tw/?p=1021
   https://github.com/ArcherHuang/LinkIt_7697/blob/master/Arduino/MQTT_MCS_Control_LED/MQTT_MCS_Control_LED.ino
  
   For more information, such as circuit diagram, material list, please visit following blog:
   https://javatoybox.blogspot.com/2019/08/iot-wifi-3.html
*/

#include <LWiFi.h>
#include <PubSubClient.h>
#include "Ultrasonic.h"
#include <String.h>


//#define WIFI_SSID "Penis"    //  your network SSID (name)
//#define WIFI_PASSWORD "DlouhyPenis666"    // your network password
#define WIFI_SSID "Galaxy S1061b2"    //  your network SSID (name)
#define WIFI_PASSWORD "blabla1234"    // your network password

#define MQTT_SERVER_IP "192.168.43.92"
#define MQTT_SERVER_PORT 1883
#define MQTT_CLIENT_ID "linklt7697_12345678"
#define MQTT_SUB_TOPIC "Measurement"    //javatoybox/linkit7697/Ultrasonic-sensor"

#define RANGER1PIN 2         //set control pin for on/off relay
Ultrasonic ultrasonic1(RANGER1PIN);
#define RANGER2PIN 3         //set control pin for on/off relay
Ultrasonic ultrasonic2(RANGER2PIN);

int status = WL_IDLE_STATUS;      // the Wifi radio's status
WiFiClient mqttClient;
PubSubClient client(mqttClient);

long lastMsg = 0;
char msg1[50];
char msg2[50];
int value = 0;


void callback(char* topic, byte* payload, unsigned int length);

void setup() {
  //Initialize serial and wait for port to open:
  Serial.begin(9600);

  // set Pin mode
  pinMode(RANGER1PIN, INPUT);
  pinMode(RANGER2PIN, INPUT);
  
  client.setServer(MQTT_SERVER_IP, MQTT_SERVER_PORT);
  client.setCallback(callback);
  connectWifi();
  connectMQTT();
}

void loop() {
  // check the network connection once every 1 seconds:
  // delay(1000);

  // check if disconnect WIFI, then reconnect
  connectWifi();
  connectMQTT();
  client.loop();

  long now = millis();
  long duration, distanceCm;
  if (now - lastMsg > 5000) {
    lastMsg = now;
    ++value;
    
    //Sensor 1
    float d1 = ultrasonic1.MeasureInCentimeters();
    String distance1 = String(d1);
    String msg_string1 = "Sensor011:" + distance1;
    msg_string1.toCharArray(msg1, 50);
    client.publish("Measurement",  msg1);
    
    //Sensor 2
    float d2 = ultrasonic2.MeasureInCentimeters();
    String distance2 = String(d2);
    String msg_string2 = "Sensor012:" + distance2;
    msg_string2.toCharArray(msg2, 50);
    client.publish("Measurement",  msg2);
  }  
}


void connectWifi() {
  // attempt to connect to Wifi network:
  while (status != WL_CONNECTED) {
    delay(5000);
    Serial.print("Attempting to connect to WPA SSID: ");
    Serial.println(WIFI_SSID);
    // Connect to WPA/WPA2 network:
    status = WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    // you're connected now, so print out the data:
    if (status = WL_CONNECTED){
      Serial.println("You're connected to Wifi network");
      printWifiData();
    }
  }
}

void printWifiData() {
  // print your WiFi shield's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  // print your MAC address:
  byte mac[6];
  char mac_str[18];
  WiFi.macAddress(mac);
  Serial.print("MAC address: ");
  sprintf(mac_str, "%02x:%02x:%02x:%02x:%02x:%02x", mac[5], mac[4], mac[3], mac[2], mac[1], mac[0]);
  Serial.println(mac_str);
  Serial.println("====================");
}

void connectMQTT() {
   // Loop until we're reconnected
  while (!client.connected())
  {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect(MQTT_CLIENT_ID))
    {
      Serial.println("connected");
      client.subscribe(MQTT_SUB_TOPIC);
    }
    else
    {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}
// Callback function
void callback(char* topic, byte* payload, unsigned int length) {   //MQTT Relay
  /*Serial.print("Input Message arrived [");
  Serial.print(MQTT_SUB_TOPIC);
  Serial.print("] ");
  Serial.print((char)payload[0]);
  if((char)payload[0] == '1'){
    digitalWrite(RANGERPIN, HIGH);
  }else if((char)payload[0] == '0'){
    digitalWrite(RANGERPIN, LOW);
  }else{
    Serial.print("value error");
  }*/
  //Serial.println();
  
}
