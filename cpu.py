"""CPU functionality."""
import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # Ram 256 bytes
        self.RAM = [0] * 256
        # MAR Memory Address Register
        self.MAR = None
        # MDR Memory Data Register
        self.MDR = None
        # stack default pointer to 0xF4?
        self.SP = 7
        # reg 8 bit
        self.reg = [0] * 8

        self.pc = 0

        self.running = False
        self.codes = {
            "LDI": 0b10000010,
            "PRN": 0b01000111,
            "HLT": 0b00000001,
            "ADD": 0b10100000,
            "MUL": 0b10100010,
            "POP": 0b01000110,
            "PUSH": 0b01000101,
            "CALL": 0b01010000,
            "RET": 0b00010001,
        }

    def load(self):
        """
        Load a program into memory.
        """
        if len(sys.argv) != 2:  # must use format ls8.py cpu to call
            print("usage: ls8.py filename")
            sys.exit()
        try:
            address = 0
            with open(sys.argv[1]) as program:
                for instruction in program:
                    if "#" in instruction:
                        instruction = instruction.split()[0]
                        if instruction == "#":
                            continue
                    else:
                        instruction = instruction.replace("\n", "")
                    self.RAM[address] = int(instruction, 2)
                    address += 1
        except FileNotFoundError:
            print(f"Couldn't open {sys.argv[1]}")
            sys.exit()

        if address == 0:
            print("no program information")
            sys.exit()

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010,  # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111,  # PRN R0
        #     0b00000000,
        #     0b00000001,  # HLT
        # ]
        #
        # for instruction in program:
        #     self.RAM[address] = instruction
        #     address += 1

    # LDI: load "immediate", store a value in a register, or "set this register to this value".
    # def LDI(self, loc, value):
    #     self.reg[loc] = value
    #     # self.pc += 3
    #
    # # PRN: a pseudo-instruction that prints the numeric value stored in a register
    # def PRN(self, loc):
    #     print(self.reg[loc])
    #     # self.pc += 2
    #
    # # HLT: halt the CPU and exit the emulator
    # def HLT(self):
    #     sys.exit()

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":  # ls8.py examples/mult.ls8
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, address):
        return self.RAM[address]

    def ram_write(self, address, value):
        self.RAM[address] = value

    def push_value(self, value):
        # Decrement SP
        self.reg[self.SP] -= 1

        # Copy the value to the SP address
        top_of_stack_addr = self.reg[self.SP]
        self.RAM[top_of_stack_addr] = value

    def pop_value(self):
        # Get the top of stack addr
        top_of_stack_addr = self.reg[self.SP]

        # Get the value at the top of the stack
        value = self.RAM[top_of_stack_addr]

        # Increment the SP
        self.reg[self.SP] += 1

        return value

    def run(self):
        # prebuilt functions
        # LDI = 0b10000010
        # PRN = 0b01000111
        # HLT = 0b00000001
        """Run the CPU."""
        self.running = True
        # self.trace(self)
        while self.running:
            ir = self.ram_read(self.pc)

            if ir == self.codes["LDI"]:
                reg_num = self.RAM[self.pc + 1]
                value = self.RAM[self.pc + 2]
                self.reg[reg_num] = value
                self.pc += 3

            elif ir == self.codes["PRN"]:
                reg_num = self.RAM[self.pc + 1]
                print(self.reg[reg_num])
                self.pc += 2

            elif ir == self.codes["HLT"]:
                sys.exit()
                # self.running = False

            elif ir == self.codes["ADD"]:
                reg_num1 = self.RAM[self.pc + 1]
                reg_num2 = self.RAM[self.pc + 2]
                self.alu("ADD", reg_num1, reg_num2)
                self.pc += 3

            elif ir == self.codes["MUL"]:
                reg_num1 = self.RAM[self.pc + 1]
                reg_num2 = self.RAM[self.pc + 2]
                self.alu("MUL", reg_num1, reg_num2)
                self.pc += 3

            elif ir == self.codes["PUSH"]:
                # Decrement SP
                self.reg[self.SP] -= 1
                # Get the reg num to push
                reg_num = self.RAM[self.pc + 1]
                # Get the value to push
                value = self.reg[reg_num]
                # Copy the value to the SP address
                top_of_stack_addr = self.reg[self.SP]
                self.RAM[top_of_stack_addr] = value
                self.pc += 2

            elif ir == self.codes["POP"]:
                # Get reg to pop into
                reg_num = self.RAM[self.pc + 1]
                # Get the top of stack addr
                top_of_stack_addr = self.reg[self.SP]
                # Get the value at the top of the stack
                value = self.RAM[top_of_stack_addr]
                # Store the value in the register
                self.reg[reg_num] = value
                # Increment the SP
                self.reg[self.SP] += 1
                self.pc += 2

            elif ir == self.codes["CALL"]:
                # Compute the return addr
                return_addr = self.pc + 2
                # Push return addr on stack
                self.push_value(return_addr)
                # Get the value from the operand reg
                reg_num = self.RAM[self.pc + 1]
                value = self.reg[reg_num]
                # Set the pc to that value
                self.pc = value

            elif ir == self.codes["RET"]:
                # return from subroutine
                # pop value from the top of the stack and store it in th pc
                return_addr = self.RAM[self.reg[self.SP]]
                self.reg[self.SP] += 1
                # Set the PC to it
                self.pc = return_addr

            else:
                print(f"Unknown instruction {ir}")
                self.trace()
                sys.exit()
