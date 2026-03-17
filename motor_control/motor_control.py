import gpiod
import time

class StepperMotor:
    def __init__(self, chip_name="gpiochip4", step_pin=17, dir_pin=27, enable_pin=24, m0_pin=16, m1_pin=22, m2_pin=21, base_steps_per_rev=200):
        self.chip = gpiod.Chip(chip_name)

        self.step = self.chip.get_line(step_pin)
        self.direction = self.chip.get_line(dir_pin)
        self.enable = self.chip.get_line(enable_pin)
        self.m0 = self.chip.get_line(m0_pin)
        self.m1 = self.chip.get_line(m1_pin)
        self.m2 = self.chip.get_line(m2_pin)

        self.step.request(consumer="stepper", type=gpiod.LINE_REQ_DIR_OUT)
        self.direction.request(consumer="stepper", type=gpiod.LINE_REQ_DIR_OUT)
        self.enable.request(consumer="stepper", type=gpiod.LINE_REQ_DIR_OUT)
        self.m0.request(consumer="stepper", type=gpiod.LINE_REQ_DIR_OUT)
        self.m1.request(consumer="stepper", type=gpiod.LINE_REQ_DIR_OUT)
        self.m2.request(consumer="stepper", type=gpiod.LINE_REQ_DIR_OUT)
        self.enable.set_value(1)  # disabled initially

        self.base_steps_per_rev = base_steps_per_rev
        self.steps_per_rev = base_steps_per_rev
        self.set_resolution(1)    # default to full step
        self.angle = 0

    def set_resolution(self, mode):
        """
        Set microstepping resolution.

        mode : int
            1 = full step, 2 = half step, 4 = quarter step, 8 = eighth step, 16 = sixteenth step, 32 = thirty-secondth step
        """
        if mode == 1:
            self.m0.set_value(0)
            self.m1.set_value(0)
            self.m2.set_value(0)
            self.steps_per_rev = self.base_steps_per_rev * 1
        elif mode == 2:
            self.m0.set_value(1)
            self.m1.set_value(0)
            self.m2.set_value(0)
            self.steps_per_rev = self.base_steps_per_rev * 2
        elif mode == 4:
            self.m0.set_value(0)
            self.m1.set_value(1)
            self.m2.set_value(0)
            self.steps_per_rev = self.base_steps_per_rev * 4
        elif mode == 8:
            self.m0.set_value(1)
            self.m1.set_value(1)
            self.m2.set_value(0)
            self.steps_per_rev = self.base_steps_per_rev * 8
        elif mode == 16:
            self.m0.set_value(0)
            self.m1.set_value(0)
            self.m2.set_value(1)
            self.steps_per_rev = self.base_steps_per_rev * 16
        elif mode == 32:
            self.m0.set_value(1)
            self.m1.set_value(1)
            self.m2.set_value(1)
            self.steps_per_rev = self.base_steps_per_rev * 32

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
        self.angle += (degrees if self.direction.get_value() == 1 else -degrees) % 360

    def shutdown(self):
        time.sleep(1)
        self.enable.set_value(1)

        self.step.release()
        self.direction.release()
        self.enable.release()
        self.m0.release()
        self.m1.release()
        self.m2.release()

    def rotate_to_angle(self, target_angle, rps):
        '''
        Rotate to a specific angle (relative to zero position)
        '''
        relative_angle = target_angle - self.angle
        move_angle = (relative_angle + 180) % 360 - 180
        self.rotate(move_angle, rps)

    def set_zero_postion(self):
        self.angle = 0

def main():
    motor = StepperMotor()

    motor.rotate(720, 3)
    time.sleep(1)
    motor.rotate(-180, 1)

    motor.shutdown()


if __name__ == "__main__":
    main()