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


def write_code(code, data, filename):
    with open(filename, "w") as f:
        for instruction in code:
            f.write(json.dumps(instruction) + "\n")
        f.write("\n")
        f.write(json.dumps({"data": data}) + "\n")


def read_code(filename):
    code = []
    data = []
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    instruction = json.loads(line)
                    instruction["opcode"] = Opcode(instruction["opcode"])
                    if "addressing_mode" in instruction:
                        instruction["addressing_mode"] = AddressingMode(instruction["addressing_mode"])

                    code.append(instruction)
                except json.JSONDecodeError:
                    data_dict = json.loads(line)
                    data = data_dict.get("data", [])

    return code, data
