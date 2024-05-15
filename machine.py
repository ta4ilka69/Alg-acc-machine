class Ports:
    def __init__(self, input_buffer):
        self.input_buffer = input_buffer
        self.output_buffer = []
        self.ports = [self.input_buffer, self.output_buffer]
class DataPath:
    data_memory_size = None
    data_memory = None
    data_reg = None
    memory_address_reg = None
    acc = None

    def __init__(self, data_memory_size,input_buffer, data_memory):
        assert data_memory_size > 0, "Memory size must be positive"
        self.data_memory_size = data_memory_size
        self.data_memory = [0]*data_memory_size
        self.data_reg = 0
        self.acc = 0
        self.output_buffer = []
        self.memory_address_reg = 0
        self.ports = Ports(input_buffer).ports
        data_memory_keys = list(data_memory.keys())
        for x in data_memory_keys:
            self.data_memory[int(x)] = data_memory[x]
        
    def mux_data_mem(self,signal):
        if signal == 0:
            return self.memory_address_reg
        return self.data_reg
    
    def mux_left_in(self,signal):
        if signal == 0:
            return self.ports[0].pop(0)
        elif signal == 1:
            return self.acc
        return 0
    def mux_right_in(self,signal,direct_load):
        if signal == 0:
            return self.data_reg
        elif signal == 1:
            return direct_load
        return 0
class ControlUnit:
    