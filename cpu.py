import numpy as np
from collections import deque
from threading import Lock

class CPU:
    _small_font_height = 5
    _large_font_height = 10
    _small_font_memory_offset = 0x00
    _large_font_memory_offset = 0x50
    
    _small_font = bytearray([
        0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
        0x20, 0x60, 0x20, 0x20, 0x70, # 1
        0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
        0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
        0x90, 0x90, 0xF0, 0x10, 0x10, # 4
        0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
        0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
        0xF0, 0x10, 0x20, 0x40, 0x40, # 7
        0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
        0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
        0xF0, 0x90, 0xF0, 0x90, 0x90, # A
        0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
        0xF0, 0x80, 0x80, 0x80, 0xF0, # C
        0xE0, 0x90, 0x90, 0x90, 0xE0, # D
        0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
        0xF0, 0x80, 0xF0, 0x80, 0x80  # F        
    ])
    
    _large_font = bytearray([
        0x7C, 0x82, 0x82, 0x82, 0x82, 0x82, 0x82, 0x82, 0x7C, 0x00, # 0
        0x08, 0x18, 0x38, 0x08, 0x08, 0x08, 0x08, 0x08, 0x3C, 0x00, # 1
        0x7C, 0x82, 0x02, 0x02, 0x04, 0x18, 0x20, 0x40, 0xFE, 0x00, # 2
        0x7C, 0x82, 0x02, 0x02, 0x3C, 0x02, 0x02, 0x82, 0x7C, 0x00, # 3
        0x84, 0x84, 0x84, 0x84, 0xFE, 0x04, 0x04, 0x04, 0x04, 0x00, # 4
        0xFE, 0x80, 0x80, 0x80, 0xFC, 0x02, 0x02, 0x82, 0x7C, 0x00, # 5
        0x7C, 0x82, 0x80, 0x80, 0xFC, 0x82, 0x82, 0x82, 0x7C, 0x00, # 6
        0xFE, 0x02, 0x04, 0x08, 0x10, 0x20, 0x20, 0x20, 0x20, 0x00, # 7
        0x7C, 0x82, 0x82, 0x82, 0x7C, 0x82, 0x82, 0x82, 0x7C, 0x00, # 8
        0x7C, 0x82, 0x82, 0x82, 0x7E, 0x02, 0x02, 0x82, 0x7C, 0x00, # 9
        0x10, 0x28, 0x44, 0x82, 0x82, 0xFE, 0x82, 0x82, 0x82, 0x00, # A
        0xFC, 0x82, 0x82, 0x82, 0xFC, 0x82, 0x82, 0x82, 0xFC, 0x00, # B
        0x7C, 0x82, 0x80, 0x80, 0x80, 0x80, 0x80, 0x82, 0x7C, 0x00, # C
        0xFC, 0x82, 0x82, 0x82, 0x82, 0x82, 0x82, 0x82, 0xFC, 0x00, # D
        0xFE, 0x80, 0x80, 0x80, 0xF8, 0x80, 0x80, 0x80, 0xFE, 0x00, # E
        0xFE, 0x80, 0x80, 0x80, 0xF8, 0x80, 0x80, 0x80, 0x80, 0x00, # F        
    ])
    
    def __init__(self, memory):
        self._memory = memory
        self._key_lock = Lock()
        self._keys = np.full(16, False)
        self._persisted_registers = np.zeros(16, dtype=np.uint8)
        self._registers = np.zeros(16, dtype=np.uint8)
        self._stack = deque()
        self._sound_timer = 0
        self._delay_timer = 0
        self._last_key_pressed = 0x0
        self._number_of_keys_pressed = 0
        self._i = 0
        self._pc = 0x200
        
        self._display_lock = Lock()
        self._create_display(64, 32)
        
        self._memory[CPU._small_font_memory_offset:CPU._small_font_memory_offset + len(self._small_font)] = self._small_font
        self._memory[CPU._large_font_memory_offset:CPU._large_font_memory_offset + len(self._large_font)] = self._large_font
        
    def execute_next_instruction(self):
        hi_instruction = self._memory[self._pc]
        lo_instruction = self._memory[self._pc + 1]
        self._pc += 2
        
        instruction = hi_instruction >> 4
        x = (hi_instruction & 0x0f)
        y = (lo_instruction >> 4)
        n = (lo_instruction & 0x0f)
        
        kk = lo_instruction
        nnn = x << 8 | kk
        
        if instruction == 0x0:
            if nnn == 0x0e0:
                self._display.fill(0)
            elif nnn >= 0x00c0 and nnn <= 0x00cf:
                self._scroll_display_down(n)
            elif nnn == 0x0ee:
                self._pc = self._stack.pop()
            elif nnn == 0x0fb:
                self._scroll_display_right()
            elif nnn == 0x0fc:
                self._scroll_display_left()
            elif nnn == 0x00fe:
                self._create_display(64, 32)
            elif nnn == 0x00ff:
                self._create_display(128, 64)
        elif instruction == 0x1:
            self._pc = nnn
        elif instruction == 0x2:
            self._stack.append(self._pc)
            self._pc = nnn
        elif instruction == 0x3:
            if self._registers[x] == kk:
                self._pc += 2
        elif instruction == 0x4:
            if self._registers[x] != kk:
                self._pc += 2
        elif instruction == 0x5:
            if self._registers[x] == self._registers[y]:
                self._pc += 2
        elif instruction == 0x6:
            self._registers[x] = kk
        elif instruction == 0x7:
            self._registers[x] += kk
        elif instruction == 0x8:
            if n == 0x0:
                self._registers[x] = self._registers[y]
            elif n == 0x1:
                self._registers[x] |= self._registers[y]
            elif n == 0x2:
                self._registers[x] &= self._registers[y]
            elif n == 0x3:
                self._registers[x] ^= self._registers[y]
            elif n == 0x4:
                result = int(self._registers[x]) + self._registers[y]
                self._registers[0xf] = 1 if result > 0xff else 0
                self._registers[x] = result & 0xff
            elif n == 0x5:
                result = int(self._registers[x]) - self._registers[y]
                self._registers[0xf] = 1 if result >= 0 else 0
                self._registers[x] = result & 0xff
            elif n == 0x6:
                self._registers[0xf] = self._registers[x] & 0x1
                self._registers[x] >>= 1
            elif n == 0x7:
                result = int(self._registers[y]) - self._registers[x]
                self._registers[0xf] = 1 if result >= 0 else 0
                self._registers[x] = result & 0xff
            elif n == 0xe:
                self._registers[0xf] = self._registers[x] >> 0x7
                self._registers[x] <<= 1
            else:
                raise IndexError("Unknown instruction")
        elif instruction == 0x9:
            if self._registers[x] != self._registers[y]:
                self._pc += 2
        elif instruction == 0xa:
            self._i = nnn
        elif instruction == 0xb:
            self._pc = nnn + self._registers[0x0]
        elif instruction == 0xc:
            self._registers[x] = np.random.randint(0, 0xff) & kk
        elif instruction == 0xd:
            self._draw_sprite(x, y, n)
        elif instruction == 0xe:
            if kk == 0x9e:
                with self._key_lock:
                    if self._keys[self._registers[x]]:
                        self._pc += 2
            elif kk == 0xa1:
                with self._key_lock:
                    if not self._keys[self._registers[x]]:
                        self._pc += 2
        elif instruction == 0xf:
            if kk == 0x07:
                self._registers[x] = self._delay_timer
            elif kk == 0x0a:
                with self._key_lock:
                    if self._number_of_keys_pressed > 0:
                        self._registers[x] = self._last_key_pressed
                    else:
                        self._pc -= 2
            elif kk == 0x15:
                self._delay_timer = self._registers[x]
            elif kk == 0x18:
                self._sound_timer = self._registers[x]
            elif kk == 0x1e:
                result = self._i + self._registers[x]
                if result > 0xfff:
                    self._registers[0xf] = 1
                self._i = result & 0xfff
            elif kk == 0x29:
                self._i = CPU._small_font_memory_offset + self._registers[x] * CPU._small_font_height
            elif kk == 0x30:
                self._i = CPU._large_font_memory_offset + self._registers[x] * CPU._large_font_height
            elif kk == 0x33:
                vx = self._registers[x]
                self._memory[self._i] = vx // 100
                self._memory[self._i + 1] = (vx // 10) % 10
                self._memory[self._i + 2] = vx % 10
            elif kk == 0x55:
                self._memory[self._i:self._i + x + 1] = self._registers[:x + 1]
            elif kk == 0x65:
                self._registers[:x + 1] = self._memory[self._i:self._i + x + 1]
            elif kk == 0x75:
                self._persisted_registers[:16] = self._registers[:16]
            elif kk == 0x85:
                self._registers[:16] = self._persisted_registers[:16]
            else:
                raise IndexError("Unknown instruction")
        else:
            raise IndexError("Unknown instruction")

    def get_display(self):
        with self._display_lock:
            return np.copy(self._display)

    def get_display_size(self):
        with self._display_lock:
            return self._display_width, self._display_height

    def press_key(self, key):
        with self._key_lock:
            if not self._keys[key]:
                self._keys[key] = True
                self._number_of_keys_pressed += 1
                self._last_key_pressed = key
    
    def release_key(self, key):
        with self._key_lock:
            if self._keys[key]:
                self._keys[key] = False
                self._number_of_keys_pressed -= 1
    
    def tick(self):
        if (self._delay_timer > 0):
            self._delay_timer -= 1
        
        if (self._sound_timer > 0):
            self._sound_timer -= 1
    
    def _create_display(self, width, height):
        with self._display_lock:
            self._display = np.zeros((width, height), dtype=np.uint32)
            self._display_height = height
            self._display_width = width
    
    def _draw_sprite(self, x, y, n):
        xStart = self._registers[x] % self._display_width
        yOffset = self._registers[y] % self._display_height
        self._registers[0xf] = 0
        
        spriteWidth = 16 if n == 0 else 8
        spriteHeight = 16 if n == 0 else n
        
        with self._display_lock:
            for row in range(spriteHeight):
                spriteRowData = \
                    self._memory[self._i + (row * 2)] << 8 | self._memory[self._i + (row * 2) + 1] if n == 0 else \
                    self._memory[self._i + row]
                
                xOffset = xStart
                
                for bit in range(spriteWidth):
                    spriteBit = (spriteRowData >> (spriteWidth - bit - 1)) & 0x1
                    pixel = self._display[(xOffset, yOffset)]
                    
                    if spriteBit > 0:
                        if pixel != 0:
                            pixel = 0
                            self._registers[0xf] = 1
                        else:
                            pixel = 0xffffffff
                    
                    self._display[(xOffset, yOffset)] = pixel
                    
                    xOffset += 1
                    
                    if xOffset >= self._display_width:
                        break
                
                yOffset += 1
                
                if yOffset >= self._display_height:
                    break
                    
    def _scroll_display_down(self, rows):
        with self._display_lock:
            np.copyto(self._display[:, rows:], self._display[:, :-rows])
            self._display[:, :rows] = np.zeros((self._display_width, rows), dtype=np.uint32)
    
    def _scroll_display_right(self):
        with self._display_lock:
            np.copyto(self._display[:-4, :], self._display[4:, :])
            self._display[-4:, :] = np.zeros((4, self._display_height), dtype=np.uint32)
    
    def _scroll_display_left(self):
        with self._display_lock:
            np.copyto(self._display[4:, :], self._display[:-4, :])
            self._display[:4, :] = np.zeros((4, self._display_height), dtype=np.uint32)
