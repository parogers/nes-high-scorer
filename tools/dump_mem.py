#!/usr/bin/env python3
#
# nes-high-scorer -- tweets out high-scores achieved in NES games
# Copyright (C) 2018  Peter Rogers (peter.rogers@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import mmap
import sys
import nes, nes.fceu
import os
import termcolor
import time

# How long between polling memory for changes
DELAY = 0.1
# How long to keep a memory location marked when it changes
MARK_TIME = 1

def fhex(n, digits):
    return '{number:0{size}x}'.format(number=n, size=digits)

def dump_line(ram, mark_time, start_addr, addr, cols):
    lst = [
        fhex(start_addr+addr, 4)
    ]
    for offset in range(cols):
        if addr+offset >= len(ram): break
        
        value = fhex(ram[addr+offset], 2)

        if mark_time and mark_time[addr+offset] > 0:
            value = termcolor.colored(value, 'red')
        
        lst.append(value)
    return lst

def dump_ram(start_addr, ram, last_ram):
    cols = 16
    addr = 0
    half_way = len(ram)//2

    while addr < half_way:
        line = (
            dump_line(ram, last_ram, start_addr, addr, cols) + 
            ['--'] + 
            dump_line(ram, last_ram, start_addr, half_way+addr, cols)
        )
        print(' '.join(line))

        addr += cols

###

start_addr = 0
stop_addr = 0x800-1

try:
    start_addr = int(sys.argv[1], 16)
except:
    pass

try:
    stop_addr = int(sys.argv[2], 16)
except:
    pass

# Start by clearing the screen
print('\033[2J')
ram = nes.fceu.open_shm()
mark_time = [0]*len(ram)
last_ram = None
last_time = None
while True:
    now = time.time()
    # Relocate the cursor and redraw overtop of the same matrix each time
    print('\033[0;0f', end='')
    ram_copy = ram[start_addr:stop_addr+1]
    dump_ram(start_addr, ram_copy, mark_time)

    if last_time != None:
        for addr, (byte, last_byte) in enumerate(zip(ram_copy, last_ram)):
            if byte != last_byte:
                mark_time[addr] = MARK_TIME

            elif mark_time[addr] > 0:
                mark_time[addr] -= now-last_time
    
    last_ram = ram_copy
    last_time = now
    time.sleep(0.1)
