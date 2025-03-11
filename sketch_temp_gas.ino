#include <DHT.h>
#include <DHT_U.h>
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
#include <MQ135.h>

#define PIN_CE 9
#define PIN_CSN 10
#define CH_NUM 0x60
#define gasPinDig 6
#define gasPinAn A0
#define R0 13.635
#define RL 1.96
#define VIN 5.0
#define SCALE 1023
#define A 3.86735
#define P -0.30866

RF24 radio(PIN_CE, PIN_CSN);
byte address[][6] = {"1Node", "2Node", "3Node", "4Node", "5Node", "6Node"};

DHT dht(2, DHT11);
MQ135 gasSensor = MQ135(gasPinAn);

int tempHum[4];

int analogValue, X;
float VOUT, RS, Y;

void setup() {
  Serial.begin(9600);
  pinMode(gasPinAn, INPUT); 
  pinMode(gasPinDig, INPUT);
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

  float ppm = gasSensor.getCO2CorrectedPPM(t, h);
  float rzero = gasSensor.getCO2CorrectedRZero(t, h);
  tempHum[0] = t;
  tempHum[1] = h;
  tempHum[2] = ppm;
  tempHum[3] = rzero;
  radio.write(&tempHum, sizeof(tempHum));
  delay(1000);

  Serial.print("PPM ");
  Serial.print(ppm);
  Serial.print(" RZERO ");
  Serial.print(rzero);
  Serial.print(" TEMP ");
  Serial.print(t);
  Serial.print(" ");
  Serial.print("HUM ");
  Serial.print(h);
  Serial.println();

}

