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
        for instruction in code:
            opcode = instruction["opcode"].name
            line = f"{opcode}"
            if "arg" in instruction:
                arg = instruction["arg"]
                if "addressing_mode" in instruction:
                    addressing_mode = instruction["addressing_mode"].name
                    line += f" {arg} {addressing_mode}" 
                else:
                    line += f" {arg}"

            if "index" in instruction:
                line += f" ; index: {instruction['index']}"

            f.write(line + "\n")


def read_code(filename):
    with open(filename) as f:
        code = json.loads(f.read())
    for instr in code:
        instr["opcode"] = Opcode(instr["opcode"])
        instr["addressing_mode"] = AddressingMode(instr["addressing_mode"])
    return code

# All data is 0 except strings
def write_data(data, filename):
    with open(filename, "w") as f:
        buffer = []
        for d in data:
            if isinstance(d, str):
                buffer.append(d)
            else:
                buffer.append("0")
        f.write("\n".join(buffer))
