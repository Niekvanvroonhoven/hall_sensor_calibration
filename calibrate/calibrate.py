from hall_sensor import sensor_functions as sf
from motor_control import motor_control as mc
import numpy as np
import matplotlib.pyplot as plt
import time

def plot_field_array(field_array):
    '''
    Documentation:
    05-03-26: Created function - Niek van Vroonhoven
    '''
    plt.figure(figsize=(12, 6))
    theta = np.linspace(0, 360, len(field_array))
    plt.plot(theta, field_array)
    plt.xlabel('Angle (degrees)')
    plt.ylabel('Magnetic Field Strength')
    plt.title('Magnetic Field Strength vs Angle')
    plt.show()


def one_cycle(degree_per_measure, motor, sensor, rps):
    '''
    Documentation:
    05-03-26: Created function - Niek van Vroonhoven
    '''
    nsamples = int(360/degree_per_measure)
    field_array = np.zeros(nsamples)

    for i in range(nsamples):
        field_array[i], _ = sensor.read_measurement()
        #time.sleep(0.01)  
        motor.rotate(degree_per_measure, rps)  #rotate the motor by degree_per_measure
 
    return field_array

def rotate_to_max(motor, field_array, degrees_per_measure):
    '''found the angle where the maximum occurs, now move the motor there'''
    max_index = np.argmax(field_array)
    max_angle = max_index * degrees_per_measure
    motor.rotate_to_angle(max_angle, rps=1) #rotating the motor to the angle where the maximum field occurs
    motor.set_zero_postion() #setting the zero position to the angle where the maximum field occurs

def main():
    motor = mc.StepperMotor()
    sensor = sf.HallSensor()
    motor.set_resolution(32) #set microstepping to 1/32 for more precision
    sensor.write_control(0b00001000) #enable auto measurement
    sensor.write_data_rate(0b00000110) #set data rate to 100Hz
    print(sensor.read_data_rate())
    degree_per_measure = 360/(200 * 4)  
    field_array = one_cycle(degree_per_measure, motor, sensor, rps=1)
    rotate_to_max(motor, field_array, degree_per_measure)
    motor.shutdown()
    plot_field_array(field_array) #plotting the field_array to find the max field and corresponding angle

if __name__ == "__main__":
    main()