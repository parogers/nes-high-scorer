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

import twitter
import os
import nes, nes.fceu
import time
import sys

#
# TODO - at the moment this only supports high-scoring in tetris, but
# the code here could be generalized to support other games
#
# To get this code running on your machine, you'll first need a twitter
# account, create an app, and generate all the credentials. This happens at:
#
# https://developer.twitter.com/
#
# Make the folder '~/.config/nes-high-scorer/' and copy + paste the
# credentials into a file there called 'secrets'. Have a look at the example
# file 'secrets.sample'.
#

from nes.tetris import DEFAULT_HIGH_SCORES
from tweeting import Tweeter
from gamestate import GameState
import argparse

# How frequently to check for a new high score
DELAY = 0.5

def get_config_dir():
    return os.path.join(os.getenv('HOME'), '.config', 'nes-high-scorer')

class HighScoreTracker:
    def __init__(self):
        self.entries = []

    def update(self, snapshot):
        """Adds new high scores to the running list, given a snapshot of
        the high-score table. This will return a list of newly added 
        entries (ignoring anything already in this table)"""

        # We only look at the parts of the high-score that are relevant
        # (eg rank can change, but it's still considered the same score if
        # other details match up)
        def essential(entry):
            return (entry.game_type, entry.name, entry.score, entry.level)
        past_entries = set(
            map(essential, self.entries + list(DEFAULT_HIGH_SCORES)))

        print('Tracked entries:')
        for arg in past_entries:
            print(repr(arg))

        new_entries = [
            entry for entry in snapshot
            if essential(entry) not in past_entries]

        print('')

        print('New entries:')
        for entry in new_entries:
            print(entry)

        if not new_entries: print('none')

        print('')

        #self.entries.update(new_entries)
        self.entries = snapshot
        return new_entries

# The NES ram (shared memory block)
ram = None
score_tracker = HighScoreTracker()
tweeter = Tweeter(os.path.join(get_config_dir(), 'secrets'))

points = []
height = []

def started():
    print('started')
    points = []
    height = []

def finishing():
    print('finishing')

def next_piece():
    print('next piece')
    #points.append(

def rom_ready():
    # Update the high-score table. Wait a bit for the ROM to initialize
    # while reading the high-score table.
    while True:
        entries = game_state.get_high_scores()
        if entries:
            score_tracker.update(entries)
            break
        time.sleep(1)

def update_high_scores():
    print('done')
    # Now we can fetch the proper entries
    entries = game_state.get_high_scores()
    new_entries = score_tracker.update(entries)

    if new_entries:
        print('*** New high scores:')
        for entry in new_entries:
            msg = tweeter.make_tweet(entry)
            print(msg)
            #tweeter.post_tweet(msg)
        print('')

game_state = GameState()
game_state.connect('started-game', started)
game_state.connect('finishing-game', finishing)
game_state.connect('finished-game', update_high_scores)
game_state.connect('next-piece', next_piece)
game_state.connect('rom-ready', rom_ready)

while True:
    if not nes.fceu.is_shm_available():
        ram = None
        game_state.rom_stopped()
        time.sleep(DELAY)
        continue

    if not ram:
        try:
            ram = nes.fceu.open_shm()
        except FileNotFoundError:
            time.sleep(DELAY)
            continue

        game_state.rom_started(ram)

    # Periodically update the game state
    game_state.update()

    # Some throttling is needed so we don't chew up CPU
    time.sleep(DELAY)
