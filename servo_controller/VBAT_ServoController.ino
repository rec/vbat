//VBAT Project - Arduino Servo Controller v0.1b 2015-08-13
//TO DO: implement function for saving home position

#include <Servo.h>
#include <math.h>

//config
boolean debug=true;

#define BAUDRATE 57600

const int buttonPin=2;
const int ledPin=13;
const int SERIAL_BUFFER_SIZE = 30;
const int radiusOfEarth = 6371; // in km
const int horServoPin=9;
const int verServoPin=10;
const float pi = 3.14159265;

//variables
Servo hor,ver;
char serial_buffer[SERIAL_BUFFER_SIZE];
float wayPointLatitude = 0, wayPointLongitude = 0, wayPointHeight = 0;	//51.265130;6.561002;500
float height=40, latitude=51.265932, longitude=6.524392;	//home position
float latitudeRadians, wayPointLatitudeRadians, longitudeRadians, wayPointLongitudeRadians;
float distanceToWaypoint, bearing, angle, deltaLatitudeRadians, deltaLongitudeRadians;

void setup() {
  Serial.begin(BAUDRATE);

  pinMode(buttonPin, INPUT);
  pinMode(ledPin, OUTPUT);

  //servo initalization
  hor.attach(horServoPin,1000,2000);	//servo timing between 1000us and 2000us!
    hor.write(90);
  ver.attach(verServoPin,1000,2000);
    ver.write(90);
}

void loop() {
  if (read_serial())
  {
    parse_serial();
	
    distanceToWaypoint=calculateDistance();
	bearing=calculateBearing();
	angle=calculateAngle();
	
	hor.write(bearing);
	ver.write(angle);

    if (debug==true)
    {
		Serial.print("Bearing: ");Serial.print(bearing,0);Serial.print(" | ");
		Serial.print("Distance: ");Serial.print(distanceToWaypoint,2);Serial.print(" | ");
		Serial.print("Angle: ");Serial.println(angle,0);
    }
  }

}

double calculateAngle() {
  float i=(distanceToWaypoint*distanceToWaypoint)+(wayPointHeight*wayPointHeight);
  float ii=sqrt(i);
  float iii=(wayPointHeight/ii);
  return asin(iii)*180/pi;
}

void radianConversion()
{
  deltaLatitudeRadians = (wayPointLatitude - latitude) * pi / 180;
  deltaLongitudeRadians = (wayPointLongitude - longitude)* pi / 180;
  latitudeRadians = latitude * pi / 180;
  wayPointLatitudeRadians = wayPointLatitude * pi / 180;
  longitudeRadians = longitude * pi / 180;
  wayPointLongitudeRadians = wayPointLongitude * pi / 180;
}

float calculateBearing()
{
  radianConversion();
  
  float y = sin(deltaLongitudeRadians) * cos(wayPointLatitudeRadians);
  float x = cos(latitudeRadians) * sin(wayPointLatitudeRadians) -
        sin(latitudeRadians) * cos(wayPointLatitudeRadians) * cos(deltaLongitudeRadians);
  
  bearing = atan2(y, x) / pi * 180;
  
  if(bearing < 0)
  {
    bearing = 360 + bearing;
  }
  
  return bearing;
}

float calculateDistance()
{
  radianConversion();
  
  float a = sin(deltaLatitudeRadians/2) * sin(deltaLatitudeRadians/2) +
          sin(deltaLongitudeRadians/2) * sin(deltaLongitudeRadians/2) * 
          cos(latitudeRadians) * cos(wayPointLatitudeRadians);
  float c = 2 * atan2(sqrt(a), sqrt(1-a)); 
  float d = radiusOfEarth * c; // distance in kilometers
  return d*1000; //distance in M
}

bool read_serial()
{
  static byte index;

  while (Serial.available())
  {
    char c = Serial.read();

    if (c >= 32 && index < SERIAL_BUFFER_SIZE - 1)
    {
      serial_buffer[index++] = c;
    }
    else if (c == '\r' || c == '\n')
    {
      serial_buffer[index] = '\0';
      index = 0;
      return true;
    }
  }

  return false;
}

void parse_serial()
{
  wayPointLatitude = atof(strtok(serial_buffer, ";"));
  wayPointLongitude = atof(strtok(NULL, ";"));
  wayPointHeight = atof(strtok(NULL, ";"));
  
  if (debug==true)
  {
	Serial.println(wayPointLatitude,6);
	Serial.println(wayPointLongitude,6);
	Serial.println(wayPointHeight,0);
  }
}
