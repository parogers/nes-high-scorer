#!/usr/bin/env python3

import nes, nes.fceu, nes.tetris

ram = nes.fceu.open_shm()
for entry in nes.tetris.get_high_scores(ram):
    print(repr(entry.name), entry.score, entry.level, entry.game_type)

print(nes.tetris.get_current_score(ram))


