#!/usr/bin/env python3

import mmap
import sys
import nes, nes.fceu
import os

try:
    addr = int(sys.argv[1], 16)
except:
    print('usage: %s addr' % os.path.basename(sys.argv[0]))
    sys.exit()

m = nes.fceu.open_shm()
print(m[addr])
