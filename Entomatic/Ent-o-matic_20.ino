/* 
 This sketch is used to read and communicate temperature data from both thermometer cables and to control the heating coils.
 Most of the sketch was gratefully ripped from https://lastminuteengineers.com/multiple-ds18b20-arduino-tutorial/
 Modified by Trees for Peace
 
 v1.5 G. Christiansson, 2020-12-08 
            - added functionality for duty-cycle to switch heating coils on and off. 
v18 G. Christiansson - 2020-12-20 - Fix dutycycle - Note - problem with the ArduinoIDE on the Raspberry - does not save the file!
             Todo: Check why the relay switches on/off even though dutycycle is 0.
	     Oke!
	     2020-12-28 - max duty_cycle = 80% - to avoid overheating when we get wrong temperature readings
v19 G Christiansson 2021-01-03 - new hardware - solid state relay - needs positive signal to open.

v19_setup Vince Busch - added thermosensor lines for #4, #5 and #6

v20 G. Christiansson - troubleshooting! 
    Observed problems:      
        #7 - one sensor cable gives -127 for all sensors. Connection problem between arduino and sensor line
        #4 - one sensor cable gives 85C often - probably a grounding problem
        #6 - seems to have inverted signal for the relay - opening when the others are closing.  Can lead to overheating.
        And... we have the #6 and #7 arduinos at the "wrong" position on the tables. Rename?
        
    Proposed solutions: 
        1. Check all cables, especially connections at the arduino side. 
        2. verify the relay problem of #6. - in that case, put an if- clause at the duty_cycle turning on/off to check for hardware ID
        3. Discard all measurements -127 and 85C.
        4. Change numbering of #6 and #7, to make the identification simpler? When should we do this?
        5. Make default temperature 25C if there is no communication with the Raspberry. (now standard is off - 0C)
        6. Max dutycycle = 50%.
	
        - Change of hardware:
	* proto7 has now relay output on pins 11-12 instead of 10-11. 
	* #5 got re-jumpered to the new standard 8-9-10 for ArduinoID
	
	All 4 are now using arduino Software ID 20, and it seems to work. 
	Note: A/B is not in the same position for all arduinos/tables. Cables are marked, except for #5.

    Observed problem - 7A heating is not sufficient with 50% to get to 28C. Adjusted to 80%.
    
    v20b - 2021-01-28 - changed prototype #7 nano to the real thing in #1 UNO. -> update 1B low power coil to the 90% dutycycle 
    - and all to have 70% as max duty cycle
    v20c - 2021-02-02 - changed to max dutycycle 100% - maybe I should do this based on the room temperature? It was very cold (-5C) last weekend...
    v20d - 2021-02-23 - changed entomatic #2 high/low after switching relay. The first relay was burned. Maybe due to the different heating cable? Let's see if it burns again.\
    
*/

int arduinoSoftwareID = 20;


#include <OneWire.h>
#include <DallasTemperature.h>

// BUS connected to Arduino on pins 2 and 3 - 
// 2021-01-05 - Switched on UNO version. (nano version has 2/3)
#define ONE_WIRE_BUS_A 3
#define ONE_WIRE_BUS_B 2

// creating separate OneWire instances for each OneWire BUS
OneWire oneWireA(ONE_WIRE_BUS_A);
OneWire oneWireB(ONE_WIRE_BUS_B);

// Pass oneWire reference to DallasTemperature library
DallasTemperature sensorsA(&oneWireA);
DallasTemperature sensorsB(&oneWireB);

// sensor addresses - will be selected depending on which arduino ID we are on
uint8_t *sensorA1;
uint8_t *sensorA2;
uint8_t *sensorA3;
uint8_t *sensorA4;
uint8_t *sensorA5;
uint8_t *sensorB1;
uint8_t *sensorB2;
uint8_t *sensorB3;
uint8_t *sensorB4;
uint8_t *sensorB5;

float setTempA = 30; // desired operating temperature
float setTempB = 29; // desired operating temperature
int powerPinA = 11; // switches relay to heating cable A // Changed 2020-12-20
int powerPinB = 12; // switches relay to heating cable B // Changed 2021-01-08 (was 10 on nano)
long previousMillis1 = 0; // used for data retrieval and communication
long previousMilliscalc = 0; // available for duty cycle calculation
long interval1 = 10000; // interval data retrieval and communication - debug mode 10s, reality 600s
long intervalcalc  = 10000; // calculation duty cycle  - debug mode 10s, reality 600s

int deviceCountA = 0;
int deviceCountB = 0;

float templistA[10];
float tempAvgA = 0;
float templistB[10];
float tempAvgB = 0;


// Duty-cycles and Power: Information and variables
// The total time length of the duty cycle is 10x duty_length_ms 
int duty_length_ms = 1000;    // Time step in the duty cycle
int duty_cycleA = 0;                // in percent: 0 = 0%, 10 = 10% >100 = 100% always on
int duty_cycleB = 0;                // in percent: 0 = 0%, 10 = 10% >100 = 100% always on
int counter_dutycycleA = 0;
int counter_dutycycleB = 0;
long previousMillisduty = 0; // for heater duty cycle action
//long intervalduty = 1000; // interval duty cycle - debug mode 1s, reality 60s
long intervalduty = 10000; // interval duty cycle - debug mode 1s, reality 10s - 2020-12-23
int MAX_DUTYCYCLE = 100;

// use pins 7-8-9 for ArdunioID. E.g. "ID 001" is created by putting pin 7 and pin 8 to ground.
// 2021-01-05 changed in v19Vince - for the UNOs to 8-9-10. 
int inPin1 = 8;
int inPin2 = 9;
int inPin3 = 10;
int arduinoID = 0;

// strict C - define all functions upfront:
void read_temps_and_log(void);
void calculate_duty_cycle(void);
void setupSensorAddresses(int arduinoID);
void duty_cycle_on_off( void );
float temp_average( float * templist, int num_temp );

void setup(void)
{
  Serial.begin(9600); // Setup serial link with Raspberry 

  // Setup digital inputs to read out the id of this Arduino - read from digital IO 8,9,10
  pinMode( inPin1, INPUT_PULLUP);
  pinMode( inPin2, INPUT_PULLUP);
  pinMode( inPin3, INPUT_PULLUP);

  int i1 = digitalRead( inPin1 );
  int i2 = digitalRead( inPin2 );
  int i3 = digitalRead( inPin3 );
  arduinoID = i1*4 + i2*2 + i3;      // Unique arduino hardware ID
   
  setupSensorAddresses( arduinoID );   // use the arduino ID to select which set of sensor addresses to use
  
  Serial.println( arduinoID );         // send to the Raspberry the ID of this Arduino
  Serial.println( arduinoSoftwareID ); // send to the raspberry the software ID number

  // workaround for the prototype nano :
  if( arduinoID == 7)
  {
     //powerPinB = 10; // switches relay to heating cable B (not 12 as in UNO version)
     // switch A/B sensor cables:
     DallasTemperature temporary;
     temporary = sensorsA;
     sensorsA = sensorsB;
     sensorsB = temporary;
  }
  sensorsA.begin(); 
  sensorsB.begin();

  pinMode(powerPinA, OUTPUT);
  pinMode(powerPinB, OUTPUT);

  // get setpoint temperatures for the two pipes from the Raspberry pi: 
  delay(2000);  // wait for 2 seconds to get the setpoint temperatures from the Raspberry (or serial monitor)  We expect: "27.4 29.8\n"
  float setA = Serial.parseFloat();
  float setB = Serial.parseFloat();
  if( setA == 0 )
  {
    // if we get no response from the Raspberry Pi - setA is 0 - keep default values defined earlier 
  }
  else
  {
  setTempA = setA;
  setTempB = setB;
  }
}

void loop(void)
{ 
    read_temps_and_log();
    
    calculate_duty_cycle();
    
    duty_cycle_on_off();
}
int logcounter = 0;
void read_temps_and_log(void)
{
    unsigned long currentMillis = millis();
  
    if(currentMillis - previousMillis1 > interval1) {
    previousMillis1 = currentMillis;
    logcounter += 1;
// print controller number

    Serial.print(arduinoID);
    Serial.print(", ");
    Serial.print(arduinoSoftwareID);
    Serial.print(", ");
  
// reading data from sensors channel A
     
    sensorsA.requestTemperatures();
    float tempsensorA1 = (sensorsA.getTempC(sensorA1));
    
    Serial.print(tempsensorA1);
    Serial.print(", ");
    float tempsensorA2 = (sensorsA.getTempC(sensorA2));
    Serial.print(tempsensorA2);
    Serial.print(", ");
    float tempsensorA3 = (sensorsA.getTempC(sensorA3));
    Serial.print(tempsensorA3);
    Serial.print(", ");
    float tempsensorA4 = (sensorsA.getTempC(sensorA4));
    Serial.print(tempsensorA4);
    Serial.print(", ");
    float tempsensorA5 = (sensorsA.getTempC(sensorA5));
    Serial.print(tempsensorA5);
    Serial.print(", ");
    deviceCountA = sensorsA.getDeviceCount();
    
    templistA[0] = tempsensorA1;
    templistA[1] = tempsensorA2;
    templistA[2] = tempsensorA3;
    templistA[3] = tempsensorA4;
    templistA[4] = tempsensorA5;

    tempAvgA = temp_average( templistA, 5);
    
    // float averageTempA = 0;
    // averageTempA = ((tempsensorA1)+(tempsensorA2)+(tempsensorA3)+(tempsensorA4)+(tempsensorA5))/deviceCountA;
    Serial.print(tempAvgA);
    Serial.print(", ");

    Serial.print(setTempA);
    Serial.print(", ");
    
    Serial.print(duty_cycleA);
    Serial.print(", ");

    
// reading data from sensors channel B

    sensorsB.requestTemperatures();
    float tempsensorB1 = (sensorsB.getTempC(sensorB1));
    Serial.print(tempsensorB1);
    Serial.print(", ");
    float tempsensorB2 = (sensorsB.getTempC(sensorB2));
    Serial.print(tempsensorB2);
    Serial.print(", ");
    float tempsensorB3 = (sensorsB.getTempC(sensorB3));
    Serial.print(tempsensorB3);
    Serial.print(", ");
    float tempsensorB4 = (sensorsB.getTempC(sensorB4));
    Serial.print(tempsensorB4);
    Serial.print(", ");
    float tempsensorB5= (sensorsB.getTempC(sensorB5));
    Serial.print(tempsensorB5);
    Serial.print(", ");

    deviceCountB = sensorsB.getDeviceCount();
    //float averageTempB = 0;
    //averageTempB = ((tempsensorB1)+(tempsensorB2)+(tempsensorB3)+(tempsensorB4)+(tempsensorB5))/deviceCountB;
    //Serial.print(averageTempB);
    //Serial.print(", ");
    
    templistB[0] = tempsensorB1;
    templistB[1] = tempsensorB2;
    templistB[2] = tempsensorB3;
    templistB[3] = tempsensorB4;
    templistB[4] = tempsensorB5;

    tempAvgB = temp_average( templistB, 5);
    
    // float averageTempA = 0;
    // averageTempA = ((tempsensorA1)+(tempsensorA2)+(tempsensorA3)+(tempsensorA4)+(tempsensorA5))/deviceCountA;
    Serial.print(tempAvgB);
    Serial.print(", ");

    Serial.print(setTempB);
    Serial.print(", ");
    Serial.print(duty_cycleB);
    Serial.print(", ");
    
    // so that we know how long the arduino is running - how many messages were sent until now
    Serial.print( logcounter );
    Serial.println(" ");
    }
}


void calculate_duty_cycle(void)
{
    float diffTemp;    
    // do something
    unsigned long currentMillis = millis();
  
    if(currentMillis - previousMilliscalc > intervalcalc) {
    previousMilliscalc = currentMillis;

    // If we get wrong input temperature data - set max duty cycle 
    // # eg: -127 or 85
    int wrongDataComeA = 0;
    int wrongDataComeB = 0;
    for( int i = 0; i<5;i++)
    {
	if( templistA[i] == 85 ) 
	{
		wrongDataComeA = 1;
	}
	if( templistA[i] == -127 ) 
	{
		wrongDataComeA = 1;
	}
    }
    if( wrongDataComeA == 1)
    { 
	duty_cycleA = MAX_DUTYCYCLE;
	return;
    }
    for( int i = 0; i<5;i++)
    {
	if( templistB[i] == 85 ) 
	{
		wrongDataComeB = 1;
	}
	if( templistB[i] == -127 ) 
	{
		wrongDataComeB = 1;
	}
    }
    if( wrongDataComeB == 1)
    { 
	duty_cycleB = MAX_DUTYCYCLE;
	return;
    }

    // calculate difference between real temperature average and setpoint temperature, base duty cycle thereupon 

    if(tempAvgA < setTempA)
    {
      // we should power the coils!
      diffTemp = setTempA-tempAvgA;
      duty_cycleA = int(floor( diffTemp * 10)) + 30;   // 10% more for each deg C we are off, plus a baseline of 30% 
      
      // max X% dutycyle
      if(duty_cycleA > MAX_DUTYCYCLE)
      {
        duty_cycleA = MAX_DUTYCYCLE;
       
      }
    }
    else  
    { // we are above the setpoint temperature:
      duty_cycleA = 0;
    }
      
    if(tempAvgB < setTempB)
    {
      // we should power the coils!
      diffTemp = setTempB-tempAvgB;
      duty_cycleB = int(floor( diffTemp * 10)) + 30;   // 10% more for each deg C we are off, plus a baseline of 30% 
      // max X%
      if(duty_cycleB > MAX_DUTYCYCLE)
      {
        duty_cycleB = MAX_DUTYCYCLE;
        if( arduinoID == 1)
        {
         // 1B has a special low-power heating coil - use higher dutycycle!
         duty_cycleB = 100; // well, we are at the max...
        }
      }
    }
    else  
    { // we are above the setpoint temperature:
      duty_cycleB = 0;
    }
   }
}



void duty_cycle_on_off( void )
{
   unsigned long currentMillis = millis();
   
   int POWERON = LOW;
   int POWEROFF = HIGH;
   if( arduinoID == 6)		// relays are opposite direction for #6
   {
   POWERON = HIGH;
   POWEROFF = LOW;
   }
   // Changed back on 2021-02-23 - switched relay (broken) to one that is on/low.
   //if( arduinoID == 2)		// relays are opposite direction for #2
   //{
   //POWERON = HIGH;
   //POWEROFF = LOW;
   //}
      
    if(currentMillis - previousMillisduty > intervalduty) {
    previousMillisduty = currentMillis;

    // step one step further in the duty_cycle:
    counter_dutycycleA++;
    counter_dutycycleB++;
    
    // if we are out of the range, restart:
    if(counter_dutycycleA > 11) {
        counter_dutycycleA = 1; 
        }
    if(counter_dutycycleB > 11) {
        counter_dutycycleB = 1; 
        }
     // should we turn on/off the relays? 
    if(duty_cycleA/10 < counter_dutycycleA)
    {
          // power to the coil!
          digitalWrite(powerPinA, POWERON); // sorry, not logical - LOW means switch the relay - we use "NO" = "Normal Open" for the power, so that it will switch off if powered off.
    } else {
        digitalWrite(powerPinA, POWEROFF);  
    }
        
    if(duty_cycleB/10 < counter_dutycycleB)
    {
          // power to the coil!
          digitalWrite(powerPinB, POWERON); // sorry, not logical - LOW means turn on the relay
    } else {
        digitalWrite(powerPinB, POWEROFF);  
    }

} // millisduty

}


float temp_average( float * templist, int num_temp )
{
  // make an average, while excluding outliers and wrong measurements. Simple formula: remove largest and smallest number. 

  float tempTotal = 0;
  int largest_index = 0;
  int smallest_index = 1;
  int i;

  float largestT = 0;
  float smallestT = 100;
  
  // find largest number:
  for( i = 0; i < num_temp; i++)
  {
    if( templist[i] > largestT)
    {
      largestT = templist[i];
      largest_index = i;
    }
  }
  // find smallest number:
  for( i = 0; i < num_temp; i++)
  {
    if(templist[i] < smallestT)
    {
      smallestT = templist[i];
      smallest_index = i;
    }
  }
  
 // sum all temperatures except largest and smallest:
 for(i = 0;i < num_temp; i ++ )
 {
  // include if i is not largest or smallest:
  if(i == largest_index) 
  { // do nothing
  } else if (i == smallest_index) 
  {
    // do nothing
  } else 
  {
    tempTotal = tempTotal + templist[i];
  }
 }
 if( largest_index == smallest_index )
 {
 // all temperatures are the same
 return( smallestT );
 }
 // return the average of the remaining temperatures
 return( tempTotal/(num_temp-2) );
}


// DallasTemperature Sensor IDs - unique for each cable set
// Addresses of sensors. These are obtained via separate sketch. Make sure the order of the sensor addresses corresponds 
// to the physical order of the sensors on the thermometer cable

// sensor-cable-set #1 - not calibrated, copied from #7, would have been #6 calibrated
uint8_t sensor1A5[8] = { 0x28, 0xAC, 0x16, 0x79, 0xA2, 0x00, 0x03, 0xBF }; // was A1
uint8_t sensor1A2[8] = { 0x28, 0x66, 0xA6, 0x79, 0xA2, 0x00, 0x03, 0xA0 }; // was A2
uint8_t sensor1A4[8] = { 0x28, 0x79, 0x34, 0x79, 0xA2, 0x00, 0x03, 0xEB }; // was A3
uint8_t sensor1A1[8] = { 0x28, 0x73, 0xA6, 0x79, 0xA2, 0x00, 0x03, 0x10 }; // was A4
uint8_t sensor1A3[8] = { 0x28, 0x9B, 0x63, 0x79, 0xA2, 0x00, 0x03, 0x68 }; // was A5
uint8_t sensor1B1[8] = { 0x28, 0x78, 0x18, 0x79, 0xA2, 0x00, 0x03, 0x05 }; // was B1
uint8_t sensor1B5[8] = { 0x28, 0x16, 0x0A, 0x79, 0xA2, 0x19, 0x03, 0x74 }; // was B2
uint8_t sensor1B2[8] = { 0x28, 0xC1, 0x5A, 0x79, 0xA2, 0x00, 0x03, 0xFE }; // was B3
uint8_t sensor1B3[8] = { 0x28, 0x51, 0xE8, 0x79, 0xA2, 0x00, 0x03, 0x83 }; // was B4
uint8_t sensor1B4[8] = { 0x28, 0x8B, 0x5A, 0x79, 0xA2, 0x00, 0x03, 0x44 }; // was B5

// sensor-cable-set #2 - #4 calibrated
uint8_t sensor2A3[8] = { 0x28, 0x42, 0xAB, 0xA6, 0x42, 0x20, 0x01, 0x07 }; // was A1
uint8_t sensor2A1[8] = { 0x28, 0x0A, 0xEA, 0x95, 0x42, 0x20, 0x01, 0x37 }; // was A2
uint8_t sensor2A2[8] = { 0x28, 0xFE, 0xEB, 0x84, 0x42, 0x20, 0x01, 0xE3 }; // was A3
uint8_t sensor2A5[8] = { 0x28, 0xC1, 0x8B, 0x91, 0x42, 0x20, 0x01, 0x82 }; // was A4
uint8_t sensor2A4[8] = { 0x28, 0xB3, 0x78, 0xE0, 0x42, 0x20, 0x01, 0xBB }; // was A5
uint8_t sensor2B2[8] = { 0x28, 0x84, 0x57, 0xF8, 0x42, 0x20, 0x01, 0x60 }; // was B1
uint8_t sensor2B5[8] = { 0x28, 0x9C, 0xE2, 0x3C, 0x42, 0x20, 0x01, 0x30 }; // was B2
uint8_t sensor2B3[8] = { 0x28, 0x65, 0x92, 0xAF, 0x42, 0x20, 0x01, 0xD0 }; // was B3
uint8_t sensor2B4[8] = { 0x28, 0xE5, 0x6A, 0x47, 0x42, 0x20, 0x01, 0xF7 }; // was B4
uint8_t sensor2B1[8] = { 0x28, 0x75, 0x01, 0x01, 0x42, 0x20, 0x01, 0xCE }; // was B5

// sensor-cable-set #3 - #5 calibrated
uint8_t sensor3A5[8] = { 0x28, 0xCA, 0x95, 0x83, 0x42, 0x20, 0x01, 0x9B }; // was A1
uint8_t sensor3A4[8] = { 0x28, 0x51, 0xBC, 0x44, 0x42, 0x20, 0x01, 0x66 }; // was A2
uint8_t sensor3A1[8] = { 0x28, 0xB1, 0x3F, 0x1B, 0x42, 0x20, 0x01, 0x88 }; // was A3
uint8_t sensor3A3[8] = { 0x28, 0xE5, 0xEE, 0x04, 0x42, 0x20, 0x01, 0x4B }; // was A4
uint8_t sensor3A2[8] = { 0x28, 0x63, 0x13, 0x02, 0x42, 0x20, 0x01, 0x50 }; // was A5
uint8_t sensor3B5[8] = { 0x28, 0x7A, 0x34, 0x00, 0x42, 0x20, 0x01, 0x33 }; // was B1
uint8_t sensor3B4[8] = { 0x28, 0xFA, 0x29, 0xE5, 0x42, 0x20, 0x01, 0x81 }; // was B2
uint8_t sensor3B2[8] = { 0x28, 0x15, 0x55, 0xE8, 0x42, 0x20, 0x01, 0x5D }; // was B3
uint8_t sensor3B3[8] = { 0x28, 0x07, 0x87, 0xFC, 0x41, 0x20, 0x01, 0x67 }; // was B4
uint8_t sensor3B1[8] = { 0x28, 0xE7, 0x75, 0xA8, 0x42, 0x20, 0x01, 0x59 }; // was B5

//sensor-cable-set #4 - #3 calibrated
uint8_t sensor4A1[8] = { 0x28, 0x69, 0x5F, 0x34, 0x42, 0x20, 0x01, 0x16 }; // was A1
uint8_t sensor4A4[8] = { 0x28, 0xE9, 0x1D, 0x34, 0x42, 0x20, 0x01, 0x96 }; // was A2
uint8_t sensor4A2[8] = { 0x28, 0xE9, 0x6B, 0x1A, 0x42, 0x20, 0x01, 0x02 }; // was A3
uint8_t sensor4A5[8] = { 0x28, 0x39, 0x06, 0x90, 0x42, 0x20, 0x01, 0xF9 }; // was A4
uint8_t sensor4A3[8] = { 0x28, 0x73, 0xC1, 0xF7, 0x42, 0x20, 0x01, 0x26 }; // was A5
uint8_t sensor4B1[8] = { 0x28, 0x92, 0xAF, 0xCD, 0x42, 0x20, 0x01, 0xD8 }; // was B1
uint8_t sensor4B5[8] = { 0x28, 0x69, 0x19, 0xEA, 0x42, 0x20, 0x01, 0x77 }; // was B2
uint8_t sensor4B4[8] = { 0x28, 0x6B, 0xEF, 0x25, 0x42, 0x20, 0x01, 0x80 }; // was B3
uint8_t sensor4B3[8] = { 0x28, 0x7B, 0x50, 0xF9, 0x42, 0x20, 0x01, 0xE8 }; // was B4
uint8_t sensor4B2[8] = { 0x28, 0x2F, 0xD9, 0x0D, 0x42, 0x20, 0x01, 0x5D }; // was B5

// sensor-cable-set #5 - #1 calibrated
uint8_t sensor5A5[8] = { 0x28, 0x12, 0x75, 0xE8, 0x42, 0x20, 0x01, 0x20 }; // was A1
uint8_t sensor5A3[8] = { 0x28, 0x72, 0xAB, 0x05, 0x42, 0x20, 0x01, 0xCB }; // was A2
uint8_t sensor5A2[8] = { 0x28, 0x55, 0xE0, 0xEF, 0x42, 0x20, 0x01, 0x33 }; // was A3
uint8_t sensor5A4[8] = { 0x28, 0xEB, 0x49, 0x01, 0x42, 0x20, 0x01, 0xBB }; // was A4
uint8_t sensor5A1[8] = { 0x28, 0xCF, 0x04, 0x21, 0x42, 0x20, 0x01, 0xA4 }; // was A5
uint8_t sensor5B5[8] = { 0x28, 0x8C, 0xE3, 0xFC, 0x42, 0x20, 0x01, 0x9F }; // was B1
uint8_t sensor5B1[8] = { 0x28, 0xD9, 0x52, 0xF6, 0x42, 0x20, 0x01, 0xC3 }; // was B2
uint8_t sensor5B4[8] = { 0x28, 0xED, 0x80, 0x37, 0x42, 0x20, 0x01, 0x99 }; // was B3
uint8_t sensor5B3[8] = { 0x28, 0x7D, 0x7A, 0xDF, 0x42, 0x20, 0x01, 0x66 }; // was B4
uint8_t sensor5B2[8] = { 0x28, 0xBF, 0xA1, 0x1E, 0x42, 0x20, 0x01, 0x0F }; // was B5

// sensor-cable-set #6 - #2 calibrated
uint8_t sensor6A2[8] = { 0x28, 0x20, 0x98, 0xF4, 0x42, 0x20, 0x01, 0xBF }; // was A1
uint8_t sensor6A3[8] = { 0x28, 0xC8, 0x36, 0xAA, 0x42, 0x20, 0x01, 0x6B }; // was A2
uint8_t sensor6A5[8] = { 0x28, 0x5A, 0x89, 0xE0, 0x42, 0x20, 0x01, 0x6F }; // was A3
uint8_t sensor6A4[8] = { 0x28, 0x39, 0x92, 0x50, 0x42, 0x20, 0x01, 0x68 }; // was A4
uint8_t sensor6A1[8] = { 0x28, 0x55, 0xEC, 0x83, 0x42, 0x20, 0x01, 0x90 }; // was A5
uint8_t sensor6B5[8] = { 0x28, 0x30, 0xEB, 0x0D, 0x42, 0x20, 0x01, 0x25 }; // was B1
uint8_t sensor6B2[8] = { 0x28, 0x32, 0xDC, 0x08, 0x42, 0x20, 0x01, 0x1F }; // was B2
uint8_t sensor6B4[8] = { 0x28, 0x06, 0xDE, 0x33, 0x42, 0x20, 0x01, 0x71 }; // was B3
uint8_t sensor6B3[8] = { 0x28, 0xA6, 0x2C, 0x14, 0x42, 0x20, 0x01, 0xFE }; // was B4
uint8_t sensor6B1[8] = { 0x28, 0xAB, 0x6A, 0x00, 0x42, 0x20, 0x01, 0xF7 }; // was B5

// sensor-cable-set #7 - prototype
uint8_t sensor7A5[8] = { 0x28, 0xAC, 0x16, 0x79, 0xA2, 0x00, 0x03, 0xBF }; // was A1
uint8_t sensor7A2[8] = { 0x28, 0x66, 0xA6, 0x79, 0xA2, 0x00, 0x03, 0xA0 }; // was A2
uint8_t sensor7A4[8] = { 0x28, 0x79, 0x34, 0x79, 0xA2, 0x00, 0x03, 0xEB }; // was A3
uint8_t sensor7A1[8] = { 0x28, 0x73, 0xA6, 0x79, 0xA2, 0x00, 0x03, 0x10 }; // was A4
uint8_t sensor7A3[8] = { 0x28, 0x9B, 0x63, 0x79, 0xA2, 0x00, 0x03, 0x68 }; // was A5
uint8_t sensor7B1[8] = { 0x28, 0x78, 0x18, 0x79, 0xA2, 0x00, 0x03, 0x05 }; // was B1
uint8_t sensor7B5[8] = { 0x28, 0x16, 0x0A, 0x79, 0xA2, 0x19, 0x03, 0x74 }; // was B2
uint8_t sensor7B2[8] = { 0x28, 0xC1, 0x5A, 0x79, 0xA2, 0x00, 0x03, 0xFE }; // was B3
uint8_t sensor7B3[8] = { 0x28, 0x51, 0xE8, 0x79, 0xA2, 0x00, 0x03, 0x83 }; // was B4
uint8_t sensor7B4[8] = { 0x28, 0x8B, 0x5A, 0x79, 0xA2, 0x00, 0x03, 0x44 }; // was B5

void setupSensorAddresses(int arduinoID)
{
  if(arduinoID == 1) 
  {
    sensorA1 = sensor1A1;
    sensorA2 = sensor1A2;
    sensorA3 = sensor1A3;
    sensorA4 = sensor1A4;
    sensorA5 = sensor1A5;
    sensorB1 = sensor1B1;
    sensorB2 = sensor1B2;
    sensorB3 = sensor1B3;
    sensorB4 = sensor1B4;
    sensorB5 = sensor1B5;
  }
  if(arduinoID == 2)  
  {
    sensorA1 = sensor2A1;
    sensorA2 = sensor2A2;
    sensorA3 = sensor2A3;
    sensorA4 = sensor2A4;
    sensorA5 = sensor2A5;
    sensorB1 = sensor2B1;
    sensorB2 = sensor2B2;
    sensorB3 = sensor2B3;
    sensorB4 = sensor2B4;
    sensorB5 = sensor2B5;
  }
  if(arduinoID == 3)  
  {
    sensorA1 = sensor3A1;
    sensorA2 = sensor3A2;
    sensorA3 = sensor3A3;
    sensorA4 = sensor3A4;
    sensorA5 = sensor3A5;
    sensorB1 = sensor3B1;
    sensorB2 = sensor3B2;
    sensorB3 = sensor3B3;
    sensorB4 = sensor3B4;
    sensorB5 = sensor3B5;
  }
   if(arduinoID == 4)  
  {
    sensorA1 = sensor4A1;
    sensorA2 = sensor4A2;
    sensorA3 = sensor4A3;
    sensorA4 = sensor4A4;
    sensorA5 = sensor4A5;
    sensorB1 = sensor4B1;
    sensorB2 = sensor4B2;
    sensorB3 = sensor4B3;
    sensorB4 = sensor4B4;
    sensorB5 = sensor4B5;
  }
   if(arduinoID == 5)  
  {
    sensorA1 = sensor5A1;
    sensorA2 = sensor5A2;
    sensorA3 = sensor5A3;
    sensorA4 = sensor5A4;
    sensorA5 = sensor5A5;
    sensorB1 = sensor5B1;
    sensorB2 = sensor5B2;
    sensorB3 = sensor5B3;
    sensorB4 = sensor5B4;
    sensorB5 = sensor5B5;
  }
  if(arduinoID == 6)  
  {
    sensorA1 = sensor6A1;
    sensorA2 = sensor6A2;
    sensorA3 = sensor6A3;
    sensorA4 = sensor6A4;
    sensorA5 = sensor6A5;
    sensorB1 = sensor6B1;
    sensorB2 = sensor6B2;
    sensorB3 = sensor6B3;
    sensorB4 = sensor6B4;
    sensorB5 = sensor6B5;
  }
    if(arduinoID == 7)  
  {
    sensorA1 = sensor7A1;
    sensorA2 = sensor7A2;
    sensorA3 = sensor7A3;
    sensorA4 = sensor7A4;
    sensorA5 = sensor7A5;
    sensorB1 = sensor7B1;
    sensorB2 = sensor7B2;
    sensorB3 = sensor7B3;
    sensorB4 = sensor7B4;
    sensorB5 = sensor7B5;
  }

}