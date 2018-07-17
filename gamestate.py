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

import itertools
import collections
import time

import nes, nes.fceu
from nes import tetris

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

    playing_tetris = False
    last_vertical_pos = -1
    last_score = -1

    def __init__(self):
        self.dispatcher = Dispatcher()

    connect = delegate('dispatcher', 'connect')
    remove = delegate('dispatcher', 'remove')
    emit = delegate('dispatcher', 'emit')

    def rom_started(self, ram):
        '''Called when the NES rom is first started'''
        self.state = self.IDLE
        self.ram = ram
        # Make sure tetris is actually being played right now
        self.playing_tetris = nes.fceu.is_tetris_running()

        if self.playing_tetris:
            print('playing tetris')

            # Wait until the score area is zeroed out so we can set our score
            # flag below without it getting clobbered.
            while ram[nes.tetris.CURRENT_SCORE_START] == 255:
                time.sleep(0.5)

            # Make the 'current score' non-zero, so we can use this to detect
            # when a new game is started. (ie gets zeroed out by the game)
            self.ram[tetris.CURRENT_SCORE_START] = 1
            self.emit('rom-ready')

    def rom_stopped(self):
        self.ram = None

    def update(self):
        '''Update this game state with a snapshot of the NES ram'''

        if not self.playing_tetris:
            return

        # Handle the case where the game goes into demo mode, which triggers
        # a start event, but never reaches the game over screen to trigger
        # the finished event. So we check for the score resetting to zero
        # which indicates a new game has started.
        score = tetris.get_current_score_bytes(self.ram)
        if (self.state == self.PLAYING and
            score == (0, 0, 0) and
            self.last_score != score):

            self.state = self.IDLE

        if self.state == self.IDLE:
            # We know a game has started when the 'current high score' memory
            # location is zeroed out. This works because the game holds the
            # value from the last game played, and playing a game always
            # yields a non-zero score. The exception is the first game ever
            # played, but that case is taken care of in 'started' above.
            if score == (0, 0, 0):
                self.state = self.PLAYING
                self.emit('started-game')

        elif self.state == self.PLAYING:
            vertical_pos = self.ram[tetris.VERTICAL_POS]
            
            if self.ram[tetris.PLAY_AREA_START] == tetris.PLAY_AREA_BAR_FILL:
                # The game is finished. Wait until the field is cleared before
                # checking high scores. (happens after the user enters one)
                self.state = self.FINISHING
                self.emit('finishing-game')

            elif vertical_pos < self.last_vertical_pos:
                # Advanced to the next piece
                self.emit('next-piece')

            self.last_vertical_pos = vertical_pos

        elif self.state == self.FINISHING:
            # When the player gets a game over, the play area fills with 'bar'
            # pieces. Then it waits for the player to enter a high score before
            # clearing those pieces again. At that point we can check for a
            # new high score entry.
            if self.ram[tetris.PLAY_AREA_START] == PLAY_AREA_EMPTY:
                self.emit('finished-game')
                self.state = self.IDLE

        self.last_score = score

    def get_high_scores(self):
        return tetris.get_high_scores(self.ram)

    def get_current_score(self):
        return tetris.get_current_score(self.ram)

    def get_play_area(self):
        ram_start = tetris.PLAY_AREA_START
        rows = tetris.PLAY_AREA_ROWS
        cols = tetris.PLAY_AREA_COLS

        ram_slice = slice(ram_start, ram_start+rows*cols)
        ram_iter = iter(self.ram[ram_slice])

        area = [
            [next(ram_iter) for col in range(cols)]
            for row in range(rows)
        ]

        return area
