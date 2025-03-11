#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

#define PIN_CE 9
#define PIN_CSN 10
#define CH_NUM 0x60
RF24 radio(PIN_CE, PIN_CSN);
int data[4];
byte address[][6] = {"1Node", "2Node", "3Node", "4Node", "5Node", "6Node"};
void setup() {
  Serial.begin(9600);
  radio.begin();
  radio.setChannel(CH_NUM);
  radio.setDataRate(RF24_250KBPS);
  radio.setPALevel(RF24_PA_MAX);
  radio.setPayloadSize(32);
  radio.openReadingPipe(1, address[0]);
  radio.powerUp();
  radio.startListening();

}

void loop() {
  if(radio.available())
  {
    radio.read(&data, sizeof(data));
    Serial.print("ТЕМПЕРАТУРА ");
    Serial.print(data[0]);
    Serial.print("°C");
    Serial.print(" ");
    Serial.print("ВЛАЖНОСТЬ ");
    Serial.print(data[1]);
    Serial.print("% ");
    Serial.print("PPM ");
    Serial.print(data[2]);
    Serial.print( " RZERO ");
    Serial.println(data[3]);
    


  }
}

