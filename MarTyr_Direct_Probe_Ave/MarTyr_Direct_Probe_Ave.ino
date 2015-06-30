unsigned long deltatime;                                // ensures enough data size for minute scale.
unsigned long previousMillis;                           // ""
int seconds =5;                                         // number of seconds between collection cycle.
int count = 300;                                        // number of data points to average over
int PIN[] = {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14};       // list of pins from which to collect data.
                                                        //
void setup()  {                                         //   
  Serial.begin(9600);                                   // opens serial port at 9600 baud
  deltatime = seconds*1000;                             // multiplies seconds by 60,000 ms (1 min).
  previousMillis = 0;                                   // no previous readings before program start.
}                                                       //
                                                        //
void loop(){                                            //
  float LIN[] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};        // creates a 15 element list of the line reading fo each pin.
  float OUT[] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};        // creates a 15 element list of pin readings to be averaged.
  int i,j,k;                                            // creates the indexing variables for the subsequnt for loops.
  for (i = 0; i <= count; i++)                          // increment index 1, the number of counts
  {                                                     //
    for (j = 0; j <= 14; j++)                           // increment index 2, the pin (channel) number.
    {                                                   //
      LIN[j] = LIN[j] + (analogRead(PIN[j])*5/1023.0);  // read in the voltage value from the specified pin.
    }                                                   //   
  }                                                     //
  if (millis() - previousMillis >= deltatime)           // If it has been more than ~ 1 second since
  {                                                     // the last collection cycle.
    previousMillis = millis();                          // sets the previous read time as now.
    for (k = 0; k <= 14; k++)                           // 15 channels
    {                                                   //
      OUT[k] = LIN[k]/(count+1);                        //
      Serial.print(OUT[k]);                             // print voltage to serial buffer.
      if (i == 14)                                      // If it's the last channel
      {                                                 //
        break;                                          // then escape the loop.
      }                                                 //
      Serial.print(",");                                // If not print a comma between last
    }                                                   // last channel voltage and next.
  }                                                     //
 Serial.flush();                                        // when done flush the serial buffer.
}                                                       // Repeat until next collection cycle..
