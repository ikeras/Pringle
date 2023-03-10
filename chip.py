import argparse
import sys
import pygame
from pygame.locals import *
import numpy as np
from emulator import Emulator
import threading

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
    
    def _create_display(self, width, height ):
        self.display_height = height
        self.display_width = width
        self.screen = pygame.display.set_mode((width * 10, height * 10))
        self.buffer = pygame.Surface((width, height))    

    def start(self):
        parser = argparse.ArgumentParser(description='Chip-8 emulator')
        parser.add_argument('rom', help='ROM (ch8) file to load - full path')
        parser.add_argument('-s', '--speed', help='Number of operations to emulate per second', default=700, type=int)
        args = parser.parse_args()
        
        emulator = Emulator()
        emulator.load_rom(args.rom)
        self.emulation_thread = threading.Thread(target=emulator.start_or_continue, args=(args.speed,))
            
        pygame.init()
        pygame.display.set_caption("Pringle Chip-8 emulator")
        width, height = emulator.get_display_size()
        self._create_display(width, height)
        
        fps = pygame.time.Clock()
        
        self.emulation_thread.start()
                    
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    emulator.stop()
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if Chip.pygame_keys_to_chip8_keys.get(event.key) is not None:
                        emulator.press_key(Chip.pygame_keys_to_chip8_keys[event.key])    
                elif event.type == pygame.KEYUP:
                    if Chip.pygame_keys_to_chip8_keys.get(event.key) is not None:
                        emulator.release_key(Chip.pygame_keys_to_chip8_keys[event.key])
                        
            width, height = emulator.get_display_size()
            if (height != self.display_height or width != self.display_width):
                self._create_display(width, height)
                            
            pygame.surfarray.blit_array(self.buffer, emulator.get_display())
            pygame.transform.scale(self.buffer, (self.display_width * 10, self.display_height * 10), self.screen)
            pygame.display.update()
            
            emulator.tick()
            fps.tick(60)
        
chip = Chip()
chip.start()