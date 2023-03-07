import argparse
import sys
import pygame
from pygame.locals import *
import numpy as np
from cpu import CPU
import time

class Chip:
    pygame_keys_to_chip8_keys = {
        pygame.K_x: 0x0,
        pygame.K_1: 0x1,
        pygame.K_2: 0x2,
        pygame.K_3: 0x3,
        pygame.K_q: 0x4,
        pygame.K_w: 0x5,
        pygame.K_UP: 0x5,
        pygame.K_e: 0x6,
        pygame.K_SPACE: 0x6,
        pygame.K_a: 0x7,
        pygame.K_LEFT: 0x7,
        pygame.K_s: 0x8,
        pygame.K_DOWN: 0x8,
        pygame.K_d: 0x9,
        pygame.K_RIGHT: 0x9,
        pygame.K_z: 0xa,
        pygame.K_c: 0xb,
        pygame.K_4: 0xc,
        pygame.K_r: 0xd,
        pygame.K_f: 0xe,
        pygame.K_v: 0xf
    }
    
    def _create_display(self, height, width):
        self.display_height = height
        self.display_width = width
        self.screen = pygame.display.set_mode((width * 10, height * 10))
        self.buffer = pygame.Surface((width, height))    

    def start(self):
        parser = argparse.ArgumentParser(description='Chip-8 emulator')
        parser.add_argument('rom', help='ROM (ch8) file to load - full path')
        parser.add_argument('-s', '--speed', help='Number of operations to emulate per second', default=700, type=int)
        args = parser.parse_args()
                
        memory = np.zeros(4 * 1024, dtype=np.uint8)
        rom = np.fromfile(args.rom, dtype=np.uint8)
        memory[0x200:0x200 + len(rom)] = rom
        
        cpu = CPU(memory)
        instructions_per_second = args.speed
        
        pygame.init()
        pygame.display.set_caption("Pringle Chip-8 emulator")
        self._create_display(cpu.display_height, cpu.display_width)
        
        fps = pygame.time.Clock()
        
        start_time = pygame.time.get_ticks()
        # instructions per second
        for i in range(instructions_per_second):
            cpu.execute_next_instruction()
        
            if (cpu.display_height != self.display_height or cpu.display_width != self.display_width):
                self._create_display(cpu.display_height, cpu.display_width)
        
        end_time = pygame.time.get_ticks()
        delay_time = (end_time - start_time) // instructions_per_second
            
        while True:
            # instructions per second
            for i in range(instructions_per_second):
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if Chip.pygame_keys_to_chip8_keys.get(event.key) is not None:
                            cpu.press_key(Chip.pygame_keys_to_chip8_keys[event.key])    
                    elif event.type == pygame.KEYUP:
                        if Chip.pygame_keys_to_chip8_keys.get(event.key) is not None:
                            cpu.release_key(Chip.pygame_keys_to_chip8_keys[event.key])
            
                cpu.execute_next_instruction()
            
                if (cpu.display_height != self.display_height or cpu.display_width != self.display_width):
                    self._create_display(cpu.display_height, cpu.display_width)
                
                pygame.time.delay(delay_time)
                
            pygame.surfarray.blit_array(self.buffer, cpu.display)
            pygame.transform.scale(self.buffer, (self.display_width * 10, self.display_height * 10), self.screen)
            pygame.display.update()
            
            cpu.tick()
            fps.tick(60)
        
chip = Chip()
chip.start()