unsigned long deltatime;                                // ensures enough data size for minute scale.
unsigned long previousMillis;                           // ""
int seconds =5;                                       // number of seconds between collection cycle.
int PIN[] = {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15};    // list of pins from which to collect data.

void setup()  {
  Serial.begin(9600);                                   // opens serial port at 9600 baud
  deltatime = seconds*1000;                            // multiplies seconds by 60,000 ms (1 min).
  previousMillis = 0;                                   // no previous readings before program start.
}

void loop(){
  if (millis() - previousMillis >= deltatime)       // If it has been more than ~ 1 second since
  {                                                     // the last collection cycle.
    previousMillis = millis();                          // sets the previous read time as now.
    int i;
    for (i = 0; i <= 14; i++)                           // 15 channels
    {
      float IN[]={analogRead(PIN[i])*5/1023.0};         // read pin A[i] and turn to voltage.
      Serial.print(IN[i]);                              // print voltage to serial buffer.
      if (i == 14)                                      // If it's the last channel
      {
        break;                                          // then escape the loop.
      }                                                 
      Serial.print(",");                                // If not print a comma between last
    }                                                   // last channel voltage and next.                                   // when done flush the serial buffer.
  }
  Serial.flush();
}                                                       // Repeat until next collection cycle..
