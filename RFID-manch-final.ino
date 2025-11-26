/*
 Copyright (c) 2014-2015 NicoHood
 See the readme for credit to other people.
 PinChangeInterrupt_TickTock
 Demonstrates how to use the library
 Connect a button/cable to pin 10/11 and ground.
 The value printed on the serial port will increase
 if pin 10 is rising and decrease if pin 11 is falling.
 PinChangeInterrupts are different than normal Interrupts.
 See readme for more information.
 Dont use Serial or delay inside interrupts!
 This library is not compatible with SoftSerial.
 The following pins are usable for PinChangeInterrupt:
 Arduino Uno/Nano/Mini: All pins are usable
 Arduino Mega: 10, 11, 12, 13, 50, 51, 52, 53, A8 (62), A9 (63), A10 (64),
               A11 (65), A12 (66), A13 (67), A14 (68), A15 (69)
 Arduino Leonardo/Micro: 8, 9, 10, 11, 14 (MISO), 15 (SCK), 16 (MOSI)
 HoodLoader2: All (broken out 1-7) pins are usable
 Attiny 24/44/84: All pins are usable
 Attiny 25/45/85: All pins are usable
 ATmega644P/ATmega1284P: All pins are usable
 */



#define  SHD2  4
#define  SHD  11



volatile long timer=0;
volatile long timer2=0;
int cind=0;
int sim1=0;
int sim2=0;
int sim3=0;
int buf[400];
int inPin=2;
volatile int index=0;
volatile int T=0;
volatile int pT=0;
volatile int first=0;
int start=0;
int end=0;
int input=0;
int tag1[]={1,1,1,1,1,0,0,1,0,0,1,0,1,0,1,0,0,0,0,0,0,1,1,1,1,0,1,1,1,1,0,1,1,0,1,0,1,1,1,1,1,10,0,0,0,1,1,0,1,0,1,1,0,0,1,0,1,1,0,0,1,1,1,1,1,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,0,0,0,0,0,0,1,1,0,1,0,1,0,1,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
int tag2[]={1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,0,0,0,0,1,0,0,0,0,1,0,0,1,0,1,0,0,0,0,0,0,1,1,1,1,0,0,1,0,1,0,0,1,1,0,1,0,0,1,1,0,0,0,0,0,0,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,1,0,1,0,1,0,1,1,0,0,1,1,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
int tag3[]={1,1,1,1,1,0,0,0,0,0,0,1,1,0,1,0,1,0,0,0,0,0,0,1,1,1,1,0,1,1,1,1,0,1,1,0,1,0,1,1,1,1,1,1,0,0,0,0,1,1,0,1,0,1,1,0,0,1,0,1,1,0,0,1,1,1,1,1,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,0,0,0,0,1,1,0,1,1,1,1,0,1,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};


void setup()
{
  Serial.begin(115200);       //Velocidad en baudios para la comunicación serial
  pinMode(inPin, INPUT);      // sets the digital pin 3 as input to sense receiver input signal
  digitalWrite(SHD,LOW);
  pinMode(SHD,OUTPUT);
  digitalWrite(SHD2,LOW);
  pinMode(SHD2,OUTPUT);


  // set pins to input with a pullup
  // attach the new PinChangeInterrupts and enable event functions below
  attachInterrupt(0, tick, CHANGE);
}

void loop() {
  // integer to count the number of prints
    if (Serial.available()>0){

    input=Serial.read();
    Serial.println(input);
    if (input==49){
      inPin=2;
      detachInterrupt(1);
      attachInterrupt(0, tick, CHANGE);
      
    }
    if (input==50){
      inPin=3;
      detachInterrupt(0);
      attachInterrupt(1, tick, CHANGE);
    }

  }
  if (index==400){
    checkbuf();
    cind=0;
    sim1=0;
    sim2=0;
    sim3=0;
    for (int j=start;j<=end;j++){
        if(buf[j]==tag1[cind]){
          sim1++;
          }
                  if(buf[j]==tag2[cind]){
          sim2++;
          }
                  if(buf[j]==tag3[cind]){
          sim3++;
          }
          cind++;
          
     }

    if (sim1>50 && sim1>sim2+20 && sim1>sim3+20){
      Serial.println(1);
      }
          else if (sim2>50 && sim2>sim1+20 && sim2>sim3+20){
      Serial.println(2);
      }
          else if (sim3>50 && sim3>sim2+20 && sim3>sim1+20){
      Serial.println(3);
      }
    index=0;
    }
}

void checkbuf(){
  int count=1;
  int val=0;
  int burst=0;
  int change=1;
  start=0;
  end=0;
  for (int i=0;i<400;i++){
      if (buf[i]==buf[i-1]){
          count++;
          val=buf[i];
          if (count==16 && end==0){
            if(start > 0){
              end=i;
              }
            burst++;
            if (burst==4){
              change=val; 
              start=i;
            }
          }

              
          }
          else{
            
            if (count<16){
                burst=0;
              }
              count=1;
            }
    }
    if (change==0){
       for (int i=0;i<400;i++){
          buf[i]= !buf[i];
        }
      
      }
  
  }

void tick() {
  timer2=timer;
  timer=micros();
  pT=T;
  T=timer-timer2;
  if (index>=400){
  }
  else{

    if (T < 150 && pT < 150 && first==0 ){
      buf[index]=buf[index-1];
      index++;
    }
    else if (T>180 && first==0){
      buf[index]= !buf[index-1];
      index++;
    }
    if(pT!=0 && first==1 && T>180){
      buf[index]=digitalRead(inPin);
      index++;
      first=0;
      }
  }
}
