from hall_sensor import I2C_UI
import numpy as np
import matplotlib.pyplot as plt

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


def one_cycle(degree_per_measure):
    '''
    Documentation:
    05-03-26: Created function - Niek van Vroonhoven
    '''
    nsamples = 360/degree_per_measure
    field_array = np.array(nsamples)

    for i in range(nsamples):
        field_array[i] = read_hall_sensor() #TODO: Create a reading function from the i2cUI

        #rotate the motor by degree_per_measure
        rotate_motor(degree_per_measure) #TODO: Create a function to rotate the motor by a certain degree
    
    #plotting the field_array to find the max field and corresponding angle
    plot_field_array(field_array) #TODO: Create a function to plot the field array and find the max field and corresponding angle
    
def rotate_motor(degree):
    '''
    Documentation:
    05-03-26: Created function - Niek van Vroonhoven
    '''
    