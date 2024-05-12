import json
from enum import Enum

MEMORY_SIZE = 4096  # could be 2**27
MAX_INT = 1 << 27 - 1
MIN_INT = -(1 << 27)
TEMPORARY_MEMORY_ADDRESS = 4095
INPUT_PORT_ADDRESS = 0
OUTPUT_PORT_ADDRESS = 1
BITMASK = 0x7FFFFFF


class Opcode(str, Enum):
    ADD = "add"
    SUB = "sub"
    MUL = "mul"
    DIV = "div"
    MOD = "mod"
    LD = "load"
    ST = "store"
    INC = "increment"
    DEC = "decrement"
    JMP = "jump"
    JZ = "jz"
    JNZ = "jnz"
    HLT = "halt"
    IN = "input"
    OUT = "output"

    def __str__(self):
        return self.value


class AddressingMode(str, Enum):
    DIRECT = "direct"
    ABSOLUTE = "absolute"
    RELATIVE = "relative"

    def __str__(self):
        return self.value


def write_code(code, filename):
    with open(filename, "w") as f:
        buffer = []
        for instruction in code:
            buffer.append(json.dump(instruction))
        f.write("\n".join(buffer))


def read_code(filename):
    with open(filename) as f:
        code = json.loads(f.read())
    for instr in code:
        instr["opcode"] = Opcode(instr["opcode"])
        instr["addressing_mode"] = AddressingMode(instr["addressing_mode"])
    return code
