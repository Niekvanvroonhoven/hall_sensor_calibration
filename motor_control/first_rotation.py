import gpiod
import time

chip = gpiod.Chip("gpiochip4") #used on the rpi5

STEP_PIN = 17 #GPIO17 pin physical pin 11
DIR_PIN = 27 #GPIO27 pin physical pin 13
ENABLE_PIN = 24 #GPIO24 pin physical pin 18

step = chip.get_line(STEP_PIN)
direction = chip.get_line(DIR_PIN)
enable = chip.get_line(ENABLE_PIN)

step.request(consumer="stepper", type=gpiod.LINE_REQ_DIR_OUT)
direction.request(consumer="stepper", type=gpiod.LINE_REQ_DIR_OUT)
enable.request(consumer="stepper", type=gpiod.LINE_REQ_DIR_OUT)
enable.set_value(1)

STEPS_PER_REV = 200 * 1 #currently using full steps


def rotate(degrees, rps):
    """
    Rotate the stepper motor.

    parameters
    ----------
    degrees : float
        Rotation angle in degrees (negative = reverse)
    rps : float
        Speed in revolutions per second
    """

    enable.set_value(0)   # enable driver
    # determine direction
    if degrees >= 0:
        direction.set_value(1)
    else:
        direction.set_value(0)

    degrees = abs(degrees)

    # number of steps required
    steps = int(STEPS_PER_REV * degrees / 360)

    # step frequency
    step_frequency = rps * STEPS_PER_REV
    delay = 1 / (2 * step_frequency)

    for _ in range(steps):
        step.set_value(1)
        time.sleep(delay)
        step.set_value(0)
        time.sleep(delay)
    enable.set_value(1)   # disable driver

def main():
    rotate(90, 1)
    time.sleep(1)
    rotate(-90, 1)

if __name__ == "__main__":
    main()
    step.release()
    direction.release()
    enable.release()