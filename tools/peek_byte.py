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

try:
    addr = int(sys.argv[1], 16)
except:
    print('usage: %s addr [count]' % os.path.basename(sys.argv[0]))
    sys.exit()

try:
    count = int(sys.argv[2])
except:
    count = 1

m = nes.fceu.open_shm()
print(" ".join(str(n) for n in m[addr:addr+count]))
