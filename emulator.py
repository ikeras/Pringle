from cpu import CPU
import numpy as np
import time

class Emulator:
    def __init__(self):
        self._memory = np.zeros(4 * 1024, dtype=np.uint8)
        self._cpu = CPU(self._memory)
        self._is_executing = False
    
    def load_rom(self, rom_path):
        rom = np.fromfile(rom_path, dtype=np.uint8)
        self._memory[0x200:0x200 + len(rom)] = rom
    
    def get_display(self):
        return self._cpu.get_display()
    
    def get_display_size(self):
        return self._cpu.get_display_size()
    
    def press_key(self, key):
        self._cpu.press_key(key)
    
    def release_key(self, key):
        self._cpu.release_key(key)
        
    def tick(self):
        self._cpu.tick()
    
    def start_or_continue(self, instructions_per_second):
        self._is_executing = True
        
        delay_time = self.get_delay_between_instructions(instructions_per_second)
        if delay_time < 0:
            delay_time = 0
        
        while self._is_executing:
            time.sleep(delay_time)
            self._cpu.execute_next_instruction()
    
    def get_delay_between_instructions(self, instructions_per_second):
        start_time = time.perf_counter()
        
        # instructions per second
        for i in range(instructions_per_second):
            self._cpu.execute_next_instruction()
                
        end_time = time.perf_counter()
        
        return (1 - (end_time - start_time)) / instructions_per_second
    
    def stop(self):
        self._is_executing = False