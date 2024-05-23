import logging
import sys

from isa import MEMORY_SIZE, AddressingMode, Opcode, read_code


class Ports:
    input = None
    output = None

    def __init__(self, input_buffer):
        self.input = 0
        self.output = 0
        self.input_buffer = input_buffer
        self.output_buffer = []

    def select_port(self, sig):
        if sig == 0:
            if len(self.input_buffer) == 0:
                raise EOFError()
            self.input = ord(self.input_buffer.pop(0))
        elif sig == 1:
            self.output_buffer.append(self.output)


class DataMemory:
    node_in = None
    node_out = None
    data_in = None

    def __init__(self, data_memory_size, data_memory):
        assert data_memory_size > 0, "Memory size must be positive"
        self.node_in = 0
        self.node_out = 0
        self.data_in = 0
        self.data_memory_size = data_memory_size
        self.data_memory = [0] * data_memory_size
        data_memory_keys = list(data_memory.keys())
        for x in data_memory_keys:
            self.data_memory[int(x)] = data_memory[x]

    def select_sig(self, sig):
        if sig == 0:
            self.node_out = self.data_memory[self.node_in]
        else:
            self.data_memory[self.node_in] = self.data_in


class Alu:
    left_in = None
    right_in = None
    out = None
    z_flag = None

    def __init__(self):
        self.left_in = 0
        self.right_in = 0
        self.mode = 0
        self.out = 0
        self.set_z_flag()
        self.ops = {
            "++": self.increment,
            "--": self.decrement,
            "+": self.plus,
            "-": self.minus,
            "*": self.multiply,
            "/": self.divide,
            "%": self.modulo,
        }

    def plus(self):
        self.out = self.left_in + self.right_in

    def minus(self):
        self.out = self.left_in - self.right_in

    def multiply(self):
        self.out = self.left_in * self.right_in

    def divide(self):
        self.out = self.left_in // self.right_in

    def modulo(self):
        self.out = self.left_in % self.right_in

    def increment(self):
        self.out = self.left_in + 1

    def decrement(self):
        self.out = self.left_in - 1

    def set_z_flag(self):
        self.z_flag = self.out == 0

    def alu_op(self, mode):
        self.ops[mode]()
        self.set_z_flag()


class DataPath:
    data_reg = None
    memory_address_reg = None
    acc = None
    alu = None
    ports = None
    data_memory = None

    def __init__(self, data_memory_size, input_buffer, data_memory):
        self.data_reg = 0
        self.acc = 0
        self.memory_address_reg = 0
        self.ports = Ports(input_buffer)
        self.alu = Alu()
        self.data_memory = DataMemory(data_memory_size, data_memory)

    def mux_data_mem(self, signal):
        if signal == 0:
            self.data_memory.node_in = self.memory_address_reg
        elif signal == 1:
            self.data_memory.node_in = self.data_reg

    def mux_left_in(self, signal):
        if signal == 0:
            self.alu.left_in = int(self.ports.input)
        elif signal == 1:
            self.alu.left_in = self.acc
        else:
            self.alu.left_in = 0

    def mux_right_in(self, signal, direct_load=0):
        if signal == 0:
            self.alu.right_in = self.data_reg
        elif signal == 1:
            self.alu.right_in = int(direct_load)
        else:
            self.alu.right_in = 0

    def latch_acc(self):
        self.acc = self.alu.out
        self.ports.output = self.acc
        self.data_memory.data_in = self.acc

    def sel_port(self, sig):
        self.ports.select_port(sig)

    def set_re_wr(self, sig):
        self.data_memory.select_sig(sig)

    def latch_data_reg(self):
        self.data_reg = self.data_memory.node_out

    def latch_memory_address_reg(self, arg):  # arg is coming from the control unit
        self.memory_address_reg = arg


    def set_op(self, mode):
        self.alu.alu_op(mode)

    def get_z_flag(self):
        return self.alu.z_flag


class ControlUnit:
    program = None
    program_counter = None
    data_path = None
    _tick = None

    def __init__(self, program, data_path: DataPath):
        self.program = program
        self.program_counter = 0
        self.data_path = data_path
        self._tick = 0
        self.ops = {
            Opcode.ADD: "+",
            Opcode.SUB: "-",
            Opcode.MUL: "*",
            Opcode.DIV: "/",
            Opcode.MOD: "%",
        }

    def tick(self):
        self._tick += 1

    def current_tick(self):
        return self._tick

    def mux_program_counter(self, sig, arg=0):
        if sig == 0:
            self.program_counter += 1
        elif sig == 1:
            self.program_counter = arg

    def decode_and_execute_controlflow_instruction(self, instr, opcode):
        if opcode is Opcode.HLT:
            raise StopIteration()
        if opcode is Opcode.JMP:
            self.mux_program_counter(1, instr["arg"])
            self.tick()
            return True
        if opcode is Opcode.JZ:
            if self.data_path.get_z_flag():
                self.mux_program_counter(1, instr["arg"])
            else:
                self.mux_program_counter(0)
            self.tick()
            return True
        if opcode is Opcode.JNZ:
            if not self.data_path.get_z_flag():
                self.mux_program_counter(1, instr["arg"])
            else:
                self.mux_program_counter(0)
            self.tick()
            return True
        return False

    def decode_and_execute_in_out_instruction(self, instr, opcode):
        if opcode is Opcode.IN:
            self.data_path.sel_port(0)
            self.data_path.mux_left_in(0)
            self.data_path.mux_right_in(2)
            self.data_path.set_op("+")
            self.data_path.latch_acc()
            self.tick()
            return True
        if opcode is Opcode.OUT:
            self.data_path.sel_port(1)
            self.tick()
            return True
        return False

    def decode_and_execute_arithmetic_instruction(self, instr, opcode):
        if opcode in self.ops.keys():
            if instr["addressing_mode"] == AddressingMode.DIRECT:
                self.data_path.mux_right_in(1, instr["arg"])  # direct_load
                self.data_path.mux_left_in(1)
            else:
                self.data_path.latch_memory_address_reg(instr["arg"])
                self.data_path.mux_data_mem(0)
                self.data_path.set_re_wr(0)
                self.data_path.latch_data_reg()
                self.data_path.mux_right_in(0)  # data_reg
                self.data_path.mux_left_in(1)  # acc
            self.data_path.set_op(self.ops[opcode])
            self.data_path.latch_acc()
            self.tick()
            return True
        return False

    def decode_and_execute_load_store_instruction(self, instr, opcode):
        if opcode is Opcode.LD:
            if instr["addressing_mode"] == AddressingMode.DIRECT:
                self.data_path.mux_right_in(1, instr["arg"])
            elif instr["addressing_mode"] == AddressingMode.ABSOLUTE:
                self.data_path.latch_memory_address_reg(instr["arg"])
                self.data_path.mux_data_mem(0)
                self.data_path.set_re_wr(0)
                self.data_path.latch_data_reg()
                self.data_path.mux_right_in(0)
            elif instr["addressing_mode"] == AddressingMode.RELATIVE:
                self.data_path.latch_memory_address_reg(instr["arg"])
                self.data_path.mux_data_mem(0)
                self.data_path.set_re_wr(0)
                self.data_path.latch_data_reg()
                self.tick()
                self.data_path.mux_data_mem(1)
                self.data_path.set_re_wr(0)
                self.data_path.latch_data_reg()
                self.data_path.mux_right_in(0)
            self.data_path.mux_left_in(2)
            self.data_path.set_op("+")
            self.data_path.latch_acc()
            self.tick()
            return True
        if opcode is Opcode.ST:
            self.data_path.latch_memory_address_reg(instr["arg"])
            self.data_path.mux_data_mem(0)
            self.data_path.set_re_wr(1)
            self.tick()
            return True
        return False

    def decode_and_execute_instruction(self):
        instr = self.program[self.program_counter]
        opcode = instr["opcode"]
        if self.decode_and_execute_arithmetic_instruction(instr, opcode):
            self.mux_program_counter(0)
            return
        if self.decode_and_execute_controlflow_instruction(instr, opcode):
            return
        if self.decode_and_execute_in_out_instruction(instr, opcode):
            self.mux_program_counter(0)
            return
        if self.decode_and_execute_load_store_instruction(instr, opcode):
            self.mux_program_counter(0)
            return
        if opcode is Opcode.DEC or opcode is Opcode.INC:
            binary_op = "--" if opcode is Opcode.DEC else "++"
            self.data_path.mux_right_in(2)
            self.data_path.mux_left_in(1)
            self.data_path.set_op(binary_op)
            self.data_path.latch_acc()
            self.tick()
            self.mux_program_counter(0)
            return

    def __repr__(self):
        state_repr = f"TICK: {self._tick:3} PC: {self.program_counter:3} ADDR: {self.data_path.data_reg} ACC:{self.data_path.acc}"
        instr = self.program[self.program_counter]
        opcode = instr["opcode"]
        instr_repr = str(opcode)
        if "arg" in instr:
            instr_repr += " {}".format(instr["arg"])
        return "{} \t{}".format(state_repr, instr_repr)


def simulation(code, input_buffer, data_memory_size, data, limit):
    data_path = DataPath(data_memory_size, input_buffer, data)
    control_unit = ControlUnit(code, data_path)
    instruction_counter = 0
    logging.debug("%s", control_unit)
    try:
        while instruction_counter < limit:
            control_unit.decode_and_execute_instruction()
            instruction_counter += 1
            logging.debug("%s", control_unit)
    except EOFError:
        logging.warning("Input buffer is empty")
    except StopIteration:
        pass
    if instruction_counter >= limit:
        logging.warning("Limit reached")
    logging.info("output_buffer: %s", repr("".join([chr(x) for x in data_path.ports.output_buffer])))
    return "".join([chr(x) for x in data_path.ports.output_buffer]), instruction_counter, control_unit.current_tick()


def main(code_file, input_file):
    code = read_code(code_file)
    with open(input_file, encoding="utf-8") as file:
        input_text = file.read()
        input_token = []
        for char in input_text:
            input_token.append(char)
    data = {}
    for string in code[1]:
        for i in range(string["start"],string["start"]+len(string["chars"])):
            data[str(i)] = string["chars"][i-string["start"]]
    output, instr_counter, ticks = simulation(
        code=code[0],
        input_buffer=input_token,
        data_memory_size=MEMORY_SIZE,
        data=data,
        limit=1000,
    )

    print("".join(output))
    print("instr_counter: ", instr_counter, "ticks:", ticks)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    assert len(sys.argv) == 3, "Wrong arguments: machine.py <code_file> <input_file>"
    _, code_file, input_file = sys.argv
    main(code_file, input_file)
