# hall_sensor_calibration
calibrating LZ with hall sensor for honours progamme 

The aim of this project is to create a proof of concept for the calibration using a hall sensor and a magnet.

The calibration function will continuously check whether the position of maximum field happens in the same place.
If this is not the case, then the position will be adjusted, and checked the next rotation.


###################
Hall sensors:
1: Not soldered correctly, creating short
2: Connects to i2c, 81% is max reading
3: Connects to i2c, 81% is max reading
4: No hall sensor
5: Not soldereed correctly, missing one connection
6: Doesnt connect to i2c
7: Connects to i2c, 81% is max reading
8: Connects to 12c, 84% is max reading

cables to connect hall sensor :
rpi pin 1 -> connector pin 1 (left)
rpi pin 6 -> connector pin 2
rpi pin 3 -> connector pin 3
rpi pin 5 -> connector pin 4


