import sys

class HallSensor:

    # --- Device configuration ---
    NMH1000_ADDR = 0x60
    I2C_BUS = 1

    # --- Registers ---
    REG_STATUS = 0x00
    REG_CONTROL = 0x01
    REG_OUT_M = 0x03
    REG_ASSERT_THRESH = 0x04
    REG_CLEAR_THRESH = 0x05
    REG_USER_ODR = 0x06
    REG_WHO_AM_I = 0x08

    REGISTERS_NAME = {
        REG_STATUS: "STATUS",
        REG_CONTROL: "CONTROL",
        REG_OUT_M: "M_OUT",
        REG_ASSERT_THRESH: "ASSERT_THRESH",
        REG_CLEAR_THRESH: "CLEAR_THRESH",
        REG_USER_ODR: "DATA_RATE",
        REG_WHO_AM_I: "WHO_AM_I"
    }

    def __init__(self, bus_num=I2C_BUS, addr=NMH1000_ADDR):
        self.bus_num = bus_num
        self.addr = addr

        try:
            import smbus2
            self.bus = smbus2.SMBus(self.bus_num)
        except ImportError:
            print("smbus2 not installed")
            sys.exit()

    # ----------------------------
    # Low-level read/write
    # ----------------------------

    def read_register(self, register):
        """Read one register."""
        try:
            return self.bus.read_byte_data(self.addr, register)
        except Exception as e:
            print(f"Read error from {self.REGISTERS_NAME.get(register,'UNKNOWN')}:", e)
            return None

    def write_register(self, register, data):
        """Write one register."""
        try:
            self.bus.write_byte_data(self.addr, register, data)
        except Exception as e:
            print(f"Write error to {self.REGISTERS_NAME.get(register,'UNKNOWN')}:", e)

    # ----------------------------
    # High level helper functions
    # ----------------------------

    def read_status(self):
        return self.read_register(self.REG_STATUS)

    def read_control(self):
        return self.read_register(self.REG_CONTROL)

    def read_measurement(self):
        """Return measurement and percentage."""
        data = self.read_register(self.REG_OUT_M)
        if data is None:
            return None, None
        percentage = round((data // 4) * 25 / 16)
        return data, percentage

    def read_assert_threshold(self):
        return self.read_register(self.REG_ASSERT_THRESH)

    def read_clear_threshold(self):
        return self.read_register(self.REG_CLEAR_THRESH)

    def read_data_rate(self):
        return self.read_register(self.REG_USER_ODR)

    def write_control(self, value):
        self.write_register(self.REG_CONTROL, value)

    def write_assert_threshold(self, value):
        self.write_register(self.REG_ASSERT_THRESH, value)

    def write_clear_threshold(self, value):
        self.write_register(self.REG_CLEAR_THRESH, value)

    def write_data_rate(self, value):
        self.write_register(self.REG_USER_ODR, value)

    def read_all_registers(self):
        """Return all registers as a dictionary."""
        result = {}
        for reg in self.REGISTERS_NAME:
            result[self.REGISTERS_NAME[reg]] = self.read_register(reg)
        return result