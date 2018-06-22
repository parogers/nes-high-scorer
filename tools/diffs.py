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
import fceu

m = fceu.open_shm()

snapshot = m[:]
tracking = set(range(len(snapshot)))
history = [[d] for d in snapshot]

while True:
    line = input("> ")

    new_snapshot = m[:]
    new_tracking = []
    for pos in tracking:
        if snapshot[pos] != new_snapshot[pos]:
            new_tracking.append(pos)
            history[pos].append(new_snapshot[pos])

    for pos in new_tracking:
        print('%04x: %d -> %d [%s]' % (
            pos, snapshot[pos], new_snapshot[pos],
            ', '.join(str(d) for d in history[pos]),
        ))
    print('***')

    snapshot = new_snapshot
    tracking = new_tracking
