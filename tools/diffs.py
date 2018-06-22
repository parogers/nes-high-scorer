#!/usr/bin/env python3

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
