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
#

import collections
import nes, nes.fceu, nes.tetris

FILL_MARKER = 0x4f
CLEAR_MARKER = 0xef

class Dispatcher:
    def __init__(self):
        self.callbacks = collections.defaultdict(list)
    
    def connect(self, signal, callback):
        self.callbacks[signal].append(callback)

    def remove(self, signal, callback):
        self.callbacks[signal].remove(callback)

    def emit(self, signal):
        for callback in self.callbacks[signal]:
            callback()

def delegate(obj_name, func_name):
    def wrapper(self, *args, **kwargs):
        obj = getattr(self, obj_name)
        func = getattr(obj, func_name)
        return func(*args, **kwargs)
    return wrapper

class GameState:
    '''Tracks the Tetris game state as the user plays the game'''

    IDLE = 0
    PLAYING = 1
    FINISHING = 2

    def __init__(self):
        self.dispatcher = Dispatcher()

    connect = delegate('dispatcher', 'connect')
    remove = delegate('dispatcher', 'remove')
    emit = delegate('dispatcher', 'emit')

    def started(self, ram):
        '''Called when the NES rom is first started'''
        self.state = self.IDLE
        # Make the 'current score' non-zero, so we can use this to detect
        # when a new game is started. (ie gets zeroed out by the game)
        ram[nes.tetris.CURRENT_SCORE_START] = 1

    def update(self, ram):
        '''Update this game state with a snapshot of the NES ram'''
        if self.state == self.IDLE:
            # We know a game has started when the 'current high score' memory
            # location is zeroed out. This works because the game holds the
            # value from the last game played, and playing a game always
            # yields a non-zero score. The exception is the first game ever
            # played, but that case is taken care of in 'started' above.
            if ram[nes.tetris.CURRENT_SCORE_START] == 0:
                self.state = self.PLAYING
                self.emit('started-game')

        elif self.state == self.PLAYING:
            if ram[nes.tetris.PLAY_AREA_START] == FILL_MARKER:
                # Make sure tetris is actually being played. This check is
                # somewhat expensive so we do that here.
                if not nes.fceu.is_tetris_running():
                    return

                # The game is finished. Wait until the field is cleared before
                # checking high scores. (happens after the user enters one)
                self.state = self.FINISHING
                self.emit('finishing-game')

        elif self.state == self.FINISHING:
            # When the player gets a game over, the play area fills with 'bar'
            # pieces. Then it waits for the player to enter a high score before
            # clearing those pieces again. At that point we can check for a
            # new high score entry.
            if ram[nes.tetris.PLAY_AREA_START] == CLEAR_MARKER:
                self.emit('finished-game')
                self.state = self.IDLE
