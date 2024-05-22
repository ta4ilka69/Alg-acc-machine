class Ports:
    input = None
    output = None
    def __init__(self, input_buffer):
        self.input = 0
        self.output = 0
        self.input_buffer = input_buffer
        self.output_buffer = []

    def select_port(self, sig, arg=0):
        if sig == 0:
            self.input = self.input_buffer.pop(0)
        elif sig == 1:
            self.output_buffer.append(self.output)


class DataMemory:
    node_in = None
    node_out = None
    def __init__(self, data_memory_size, data_memory):
        assert data_memory_size > 0, "Memory size must be positive"
        self.node_in = 0
        self.node_out = 0
        self.data_memory_size = data_memory_size
        self.data_memory = [0] * data_memory_size
        data_memory_keys = list(data_memory.keys())
        for x in data_memory_keys:
            self.data_memory[int(x)] = data_memory[x]

    def select_sig(self, sig, data_in = 0):
        if sig == 0:
            self.node_out = self.data_memory[self.node_in]
        else:
            self.data_memory[self.node_in] = self.data_in



class DataPath:
    data_reg = None
    memory_address_reg = None
    acc = None
    alu_right = 0
    alu_left = 0
    alu_mode = None
    alu_out = None
    ports = None
    data_memory = None

    def __init__(self, data_memory_size, input_buffer, data_memory):
        self.data_reg = 0
        self.acc = 0
        self.memory_address_reg = 0
        self.ports = Ports(input_buffer)
        self.data_memory = DataMemory(data_memory_size, data_memory)

    def mux_data_mem(self, signal):
        if signal == 0:
            self.data_memory.node_in = 

    def mux_left_in(self, signal):
        if signal == 0:
            self.alu_left = self.ports.select_port(signal)
        elif signal == 1:
            self.alu_left = self.acc
        else:
            self.alu_left = 0

    def mux_right_in(self, signal, direct_load):
        if signal == 0:
            self.alu_right = self.data_reg
        elif signal == 1:
            self.alu_right = direct_load
        else:
            self.alu_right = 0

    def latch_acc(self):
        self.acc = self.alu_out

    def sel_port(self, sig):
        pass


class ControlUnit:
    pass
