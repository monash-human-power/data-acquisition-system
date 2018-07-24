typedef struct
{
  double latitude;
  double longitude;
  double altitude;
  double course;
  int time;
  double speed;
  int satellites;
} GPS;

typedef struct
{
  float x;
  float y;
  float z;
} Accelerometer;

typedef struct 
{
  float x;
  float y;
  float z;
} Gyroscope;

typedef struct 
{
  float celsius;
  float fahrenheit;
} Temperature;