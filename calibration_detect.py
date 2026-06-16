from hall_sensor import sensor_functions as sf
import numpy as np


""" 
Main idea: 
    - Input is the predicted angle of the motor (Beta) 
    - Output is an array with tuples of (angle, field_strength)
    - Compare where the maximum is (Beta) with the known position of the maximum (Alpha)
    - Send the offset through to the computer
"""

def read_new_values(predicted_angle, handler, previous_values):
    """
    Reads the new values from the sensor and returns an array of tuples (angle, field_strength)
    """
    # Read the measurement from the sensor
    measurement,_ = handler.read_measurement() #read the value of the hall sensor at the predicted angle 
    if measurement is None:
        print("Error while reading the measurement, returning previous values")
        return previous_values
    angle_field_tuple = (predicted_angle, measurement)
    previous_values[predicted_angle] = angle_field_tuple #Changing value of angle and field strength to the new measurement 
    return previous_values

def check_new_peak(previous_values, threshhold):
    """
    Finding the maximum and the angle
    """
    angles = [x[0] for x in previous_values]
    measurements = [x[1] for x in previous_values] 
    idx_max = np.argmax(measurements) #finds the index of the maximum value 
    if measurements[idx_max] > threshhold:
        beta = angles[idx_max] #Angle of the max
        return beta
    else: 
        beta = None #No new angle has been found
        return beta #may be set to zero? because the angle does not have to be updated. ill see

#defining when to use the checking max logic
#should be done when there is a turn back! so when the change in angle has the opposite sign to previous change in angle 

def main(delta_angle_old, previous_angle, predicted_angle, handler, previous_values, threshold):
    """
    Main function to read the new beta with the logic to do this correctly
    """

    updated_values = read_new_values(predicted_angle, handler, previous_values)

    delta_angle = predicted_angle - previous_angle
    #TODO: this logic should be revised
    if (delta_angle*delta_angle_old < 0 or abs(delta_angle) == 359): #opposite sign, so there is a change in direction or a full turn has been made, check
        beta = check_new_peak(updated_values, threshold)
    else:
        beta = None #no new angle has been checked for


    #sending the drift in the angle to the computer
    if beta != None:
        adjustment = -beta #turn motors in the opposite direction of the drift
    else:
        adjustment = 0 #no adjustment needed
    
    return beta, adjustment, updated_values, delta_angle

if __name__ == "__main__":
    #example
    handler = sf.HallSensor()
    predicted_angle = motor.get_angle()
    previous_values = np.array((0,0)*360) # Assuming 360 possible angles
    delta_angle_old = 0
    previous_angle = 0
    while True:
        beta, adjustment, updated_values, delta_angle = main(delta_angle_old, previous_angle, predicted_angle, handler, previous_values, threshold=0.5)
        #update the values logic
        delta_angle_old = delta_angle
        previous_angle = predicted_angle
        previous_values = updated_values