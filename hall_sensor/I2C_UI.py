import time
import sys

# --- NMH1000 Register Definitions ---
NMH1000_ADDR = 0x60 
I2C_BUS = 1

# Registers
REG_STATUS = 0x00
REG_CONTROL = 0x01
REG_OUT_M = 0x03
REG_ASSERT_THRESH = 0x04
REG_CLEAR_THRESH = 0x05
REG_USER_ODR = 0x06
REG_WHO_AM_I = 0x08

REGISTERS_NAME = {REG_STATUS: "STATUS",
             REG_CONTROL: "CONTROL",
             REG_OUT_M: "M_OUT",
             REG_ASSERT_THRESH: "ASSERT_THRESH",
             REG_CLEAR_THRESH: "CLEAR_TRESH",
             REG_USER_ODR: "DATA_RATE",
            }

# --- I2C Handler ---
class I2CHandler:
    def __init__(self, bus_num, addr):
        self.bus_num = bus_num
        self.addr = addr
        self.bus = None
        try:
            import smbus2
            self.bus = smbus2.SMBus(self.bus_num)
        except ImportError:
            print("SMBus not found.")
            sys.exit()

    def read_byte(self, register):
        try:
            return self.bus.read_byte_data(self.addr, register)
        except Exception as e:
            print(f"Read Error 0x{register:02X}: {e}")
            return 0x00

    def write_byte(self, register, data):
        try:
            self.bus.write_byte_data(self.addr, register, data)
            return True
        except Exception:
            return False

def delete_line(num_lines):
    for i in range(num_lines):
        sys.stdout.write('\x1b[1A') # Move cursor up one line
        sys.stdout.write('\x1b[2K') # Clear the entire line
        sys.stdout.flush()

def get_i2c_data():
    while True:
        data = input("Enter 8-bit I2C data (only 0 or 1): ").strip()

        # Check length and allowed characters
        if len(data) == 8 and all(bit in "01" for bit in data):
            data_int = int(data, 2)
            delete_line(1)
            return data_int
        else:
            print("Invalid input. Please enter exactly 8 bits consisting of only 0s and 1s.")

def read_or_write():
    '''
    checks if the user would like to read, write or quit on the I2C channel

    :return read: will be 'True' when the user want to read and 'False' when the user wants to write
    '''

    text = ""
    while text not in ["R", "W", "Q"]:
        text = input("Would you want to read (type 'R'), write (type 'W') or quit (type 'Q')? ").strip().upper()
    delete_line(1)
    if text == "Q": sys.exit()

    return True if text == "R" else False

def user_read(handler):
    '''
    Asks the user what register it wants to read and then returns the data in that register

    :return data: 8 bit data from the register chosen
    '''
    REGISTERS = {1: REG_STATUS,
                2: REG_CONTROL,
                3: REG_OUT_M,
                4: REG_ASSERT_THRESH,
                5: REG_CLEAR_THRESH,
                6: REG_USER_ODR,
            }

    text = ""
    while text not in range(1, 8):
        text = int(input(f"What register would you want to read? \n STATUS (1) \n CONTROL  (2) \n M_OUT (3) \n ASSERT_THRESH (4) \n CLEAR_TRESH (5) \n DATA_RATE (6) \n ALL_REGISTERS (7) "))
    delete_line(8)

    if text == 7:
        for i in range(1, 7):
            reg = REGISTERS[i]
            data = handler.read_byte(reg)
            print(f"The data in register {REGISTERS_NAME[reg]} is", format(data, "08b"))
        return
    
    if text == 3:
        reg = REGISTERS[text]
        data = handler.read_byte(reg)
        percentage = round((data//4)*25/16)
        print(f"The data in register {REGISTERS_NAME[reg]} is", format(data, "08b"), "Which is %d%% of max measurement." % percentage)
        return
    
    reg = REGISTERS[text]
    data = handler.read_byte(reg)
    print(f"The data in register {REGISTERS_NAME[reg]} is", format(data, "08b"))
    return

def user_write(handler):
    '''
    Asks what register the user would like to write to and then what data.
    '''
    REGISTERS = {1: REG_STATUS,
            2: REG_CONTROL,
            3: REG_OUT_M,
            4: REG_ASSERT_THRESH,
            5: REG_CLEAR_THRESH,
            6: REG_USER_ODR,
        }
    
    text = ''
    while text not in range(1, 7):
        text = int(input(f"What register would you want to write to? \n STATUS (1) \n CONTROL  (2) \n M_OUT (3) \n ASSERT_THRESH (4) \n CLEAR_TRESH (5) \n DATA_RATE (6) "))
    delete_line(7)

    reg = REGISTERS[text]
    data = get_i2c_data()
    handler.write_byte(reg, data)

    data_read = handler.read_byte(reg)
    print(f"The data written in register {REGISTERS_NAME[reg]} is", format(data_read, "08b"))
    return 

def ask_for_input(handler):
    read = read_or_write()
    if read:
        user_read(handler)
    else:
        user_write(handler)
    return


# --- Main Entry ---
if __name__ == "__main__":
    handler = I2CHandler(I2C_BUS, NMH1000_ADDR)
    print("start")
    while True:
        ask_for_input(handler)

    

