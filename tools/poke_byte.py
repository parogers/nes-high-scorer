#!/usr/bin/env python3

import mmap
import sys
import nes, nes.fceu
import os

try:
    addr = int(sys.argv[1], 16)
    data = int(sys.argv[2])
except:
    print('usage: %s addr byte' % os.path.basename(sys.argv[0]))
    sys.exit()

m = nes.fceu.open_shm()
m[addr] = data
