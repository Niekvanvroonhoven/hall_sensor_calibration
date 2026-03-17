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

cables to connect motor and driver:
!! 100uF capacitor between positive and ground rail !!
rpi pin 6 - > ground rail
rpi pin 1  -> DRV8825 pin 6 (sleep) & DRV8825 pin 5 (reset)
rpi pin 11 -> DRV8825 pin 7 (step)
rpi pin 13 -> DRV8825 pin 8 (dir)
rpi pin 18 -> DRV8825 pin 1 (enable)
rpi pin 40 -> DRV8825 pin 4 (m2)
rpi pin 38 -> DRV8825 pin 3 (m1)
rpi pin 36 -> DRV8825 pin 2 (m0)
DRV8825 pin 16 -> positive terminal power supply
DRV8825 pin 15 & 9 -> ground rail
DRV8825 pin 13 & 14 -> motor coil 1
DRV8825 pin 11 & 12 -> motor coil 2
