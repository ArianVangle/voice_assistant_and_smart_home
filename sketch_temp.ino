#include <DHT.h>
#include <DHT_U.h>
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

#define PIN_CE 9
#define PIN_CSN 10
#define CH_NUM 0x60
RF24 radio(PIN_CE, PIN_CSN);
byte address[][6] = {"1Node", "2Node", "3Node", "4Node", "5Node", "6Node"};
DHT dht(2, DHT11);
int tempHum[2];

void setup() {
  Serial.begin(9600);
  radio.begin();
  radio.setDataRate(RF24_250KBPS);
  radio.setPALevel(RF24_PA_MAX);
  radio.openWritingPipe(address[0]);
  radio.setChannel(0x60);
  dht.begin(); 
  radio.powerUp();
  radio.stopListening();
}

void loop() {
  int h = dht.readHumidity();
  int t = dht.readTemperature();
  tempHum[0] = t;
  tempHum[1] = h;
  radio.write(&tempHum, sizeof(tempHum));
  delay(1000);
}
