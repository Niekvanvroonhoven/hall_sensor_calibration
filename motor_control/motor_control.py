import gpiod
import time

class StepperMotor:
    def __init__(self, chip_name="gpiochip4", step_pin=17, dir_pin=27, enable_pin=24, steps_per_rev=200):
        self.chip = gpiod.Chip(chip_name)

        self.step = self.chip.get_line(step_pin)
        self.direction = self.chip.get_line(dir_pin)
        self.enable = self.chip.get_line(enable_pin)

        self.step.request(consumer="stepper", type=gpiod.LINE_REQ_DIR_OUT)
        self.direction.request(consumer="stepper", type=gpiod.LINE_REQ_DIR_OUT)
        self.enable.request(consumer="stepper", type=gpiod.LINE_REQ_DIR_OUT)

        self.enable.set_value(1)  # disabled initially

        self.steps_per_rev = steps_per_rev

    def rotate(self, degrees, rps):
        """
        Rotate the stepper motor.

        degrees : float
            Rotation angle in degrees (negative = reverse)
        rps : float
            Speed in revolutions per second
        """

        self.enable.set_value(0)

        if degrees >= 0:
            self.direction.set_value(1)
        else:
            self.direction.set_value(0)

        degrees = abs(degrees)

        steps = int(self.steps_per_rev * degrees / 360)

        step_frequency = rps * self.steps_per_rev
        delay = 1 / (2 * step_frequency)

        for _ in range(steps):
            self.step.set_value(1)
            time.sleep(delay)
            self.step.set_value(0)
            time.sleep(delay)

    def shutdown(self):
        time.sleep(1)
        self.enable.set_value(1)

        self.step.release()
        self.direction.release()
        self.enable.release()


def main():
    motor = StepperMotor()

    motor.rotate(720, 3)
    time.sleep(1)
    motor.rotate(-180, 1)

    motor.shutdown()


if __name__ == "__main__":
    main()