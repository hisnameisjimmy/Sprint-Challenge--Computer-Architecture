"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
PUSH = 0b01000101
MUL = 0b10100010
POP = 0b01000110
ADD = 0b10100000
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110
CMP = 0b10100111

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.registers = [0] * 8
        self.pc = 0
        self.registers[7] = 0xF4  #244
        self.flags = 0b00000000
        self.branch_table = {
            HLT: self.hlt,
            LDI: self.ldi,
            PRN: self.prn,
            JMP: self.jmp,
            JEQ: self.jeq,
            JNE: self.jne,
            PUSH: self.push,
            POP: self.pop,
            MUL: self.alu,
            ADD: self.alu,
            CMP: self.alu
        }

    def load(self):
        """Load a program into memory."""
                # For now, we've just hardcoded a program:

        if len(sys.argv) != 2:
            print("Failed to pass both filenames")
            print("Usage is python3 fileio.py [secondfilename.py]")
            sys.exit()

        
        address = 0

        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    split_line = line.split("#")[0]
                    stripped_split_line = split_line.strip()

                    if stripped_split_line != "":
                        command = int(stripped_split_line, 2)
                        
                        # load command into memory
                        self.ram[address] = command

                        address += 1
        except FileNotFoundError:
            print(f"Error from {sys.argv[0]}: {sys.argv[1]} - Not Found")
            sys.exit()
            
    def ram_read(self, MAR):  #MAR is memory address register
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):  #memory data register
        self.ram[MAR] = MDR

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == ADD:
            self.registers[reg_a] += self.registers[reg_b]
        elif op == MUL:
            self.registers[reg_a] *= self.registers[reg_b]
        elif op == CMP:
            if self.registers[reg_a] < self.registers[reg_b]:
                self.flags = 0b00000100
            if self.registers[reg_a] > self.registers[reg_b]:
                self.flags = 0b00000010
            if self.registers[reg_a] == self.registers[reg_b]:
                self.flags = 0b00000001
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        self.running = True

        while self.running:
            IR = self.ram_read(self.pc)  #Instruction Register
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            num_operands = IR >> 6
            self.pc += 1 + num_operands
            is_alu_op = ((IR >> 5) & 0b001) == 1 # gives truth value of 0 or 1 with masking
            if is_alu_op:
                self.alu(IR, operand_a, operand_b)
            else:
                self.branch_table[IR](operand_a, operand_b)
                

    def hlt(self, operand_a, operand_b):
        self.running = False

    def ldi(self, operand_a, operand_b):
        self.registers[operand_a] = operand_b

    def prn(self, operand_a, operand_b):
        print(self.registers[operand_a])

    def push(self, operand_a, operand_b):
        self.registers[7] -= 1
        value = self.registers[operand_a]
        SP = self.registers[7] # Stack pointer
        self.ram_write(SP, value)

    def pop(self, operand_a, operand_b):
        SP = self.registers[7]
        value = self.ram_read(SP)
        register_address = self.ram[self.pc + 1]
        self.registers[operand_a] = value
        self.registers[7] += 1

    def jmp(self, operand_a, operand_b):
        self.pc = self.registers[operand_a]

    def jeq(self, operand_a, operand_b):
        if (self.flags == 1):
            self.pc=self.registers[operand_a]

    def jne(self, operand_a, operand_b):
        if (self.flags != 1):
            self.pc = self.registers[operand_a]
