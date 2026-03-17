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


def one_cycle(degree_per_measure, motor, sensor):
    '''
    Documentation:
    05-03-26: Created function - Niek van Vroonhoven
    '''
    nsamples = int(360/degree_per_measure)
    field_array = np.zeros(nsamples)
    RPS = 0.1

    for i in range(nsamples):
        field_array[i], _ = sensor.read_measurement()
        time.sleep(0.01)  
        motor.rotate(degree_per_measure, RPS)  #rotate the motor by degree_per_measure
 
    plot_field_array(field_array) #plotting the field_array to find the max field and corresponding angle
    
def main():
    motor = mc.StepperMotor()
    sensor = sf.HallSensor()
    sensor.write_control(0b00001000)
    print(sensor.read_control())
    degree_per_measure = 360/200
    one_cycle(degree_per_measure, motor, sensor)
    motor.shutdown()

if __name__ == "__main__":
    main()