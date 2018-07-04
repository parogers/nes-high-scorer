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
import json
import os
import nes, nes.fceu, nes.tetris
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

from nes.tetris import HighScoreEntry

# How frequently to check for a new high score
DELAY = 2

FILL_MARKER = 0x4f
CLEAR_MARKER = 0xef

def get_config_dir():
    return os.path.join(os.getenv('HOME'), '.config', 'nes-high-scorer')

class Tweeter:
    def __init__(self, secrets_path):
        self.secrets_path = secrets_path
        # Santiy check for secrets
        self.read_secrets()
    
    def read_secrets(self):
        return json.loads(open(self.secrets_path).read())

    def post_tweet(self, msg):
        secrets = self.read_secrets()
        api = twitter.Api(
            consumer_key=secrets['consumer_key'],
            consumer_secret=secrets['consumer_secret'],
            access_token_key=secrets['access_token_key'],
            access_token_secret=secrets['access_token_secret'])
        api.VerifyCredentials()

        status = api.PostUpdate(msg)
        print(status, status.text)

    def make_tweet(self, entry):
        # Fix the name by stripping off trailing dashes (default when you
        # enter a high-score)
        name = entry.name.strip()
        while name and name.endswith('-'):
            name = name[:-1]

        # bytes([0xF0, 0x9F, 0x8E, 0x86])
        fmt = 'Congrats {}!!! You scored {:,} pts and reached L{} ({}-type) #tetris'
        return fmt.format(
            name, entry.score, entry.level, entry.game_type)

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
            map(essential, self.entries+list(nes.tetris.DEFAULT_HIGH_SCORES)))

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
# Whether we think the player has just finished a game (and therefore
# should check the high-score table for updates)
finishing_game = False
score_tracker = HighScoreTracker()
tweeter = Tweeter(os.path.join(get_config_dir(), 'secrets'))

while True:
    if not nes.fceu.is_shm_available():
        ram = None
        time.sleep(DELAY)
        continue

    if not ram:
        try:
            ram = nes.fceu.open_shm()
        except FileNotFoundError:
            time.sleep(DELAY)
            continue

        # Update the high-score table. Wait a bit for the ROM to initialize
        # while reading the high-score table.
        finishing_game = False
        while True:
            entries = nes.tetris.get_high_scores(ram)
            if entries:
                score_tracker.update(entries)
                break
            time.sleep(1)

    # Either the game is waiting to be played, or the game is currently
    # being played. Wait for the game field to fill with 'bar pieces'
    # which indicate the game is over.
    if not finishing_game and ram[nes.tetris.PLAY_AREA_START] == FILL_MARKER:
        # The game is finished. Wait until the field is cleared before
        # checking high scores. (happens after the user enters one)
        print('finishing game')
        finishing_game = True

    # When the player gets a game over, the play area fills with 'bar'
    # pieces. Then it waits for the player to enter a high score before
    # clearing those pieces again. At that point we can check for a
    # new high score entry.
    if finishing_game and ram[nes.tetris.PLAY_AREA_START] == CLEAR_MARKER:
        # Make sure tetris is actually being played. This check is somewhat
        # expensive so we do that here.
        if not nes.fceu.is_tetris_running():
            time.sleep(DELAY)
            continue

        print('game is finally finished')

        # Now we can fetch the proper entries
        entries = nes.tetris.get_high_scores(ram)
        new_entries = score_tracker.update(entries)

        if new_entries:
            print('*** New high scores:')
            for entry in new_entries:
                msg = tweeter.make_tweet(entry)
                print(msg)
                #tweeter.post_tweet(msg)
            print('')

        finishing_game = False

    # Some throttling is needed
    time.sleep(DELAY)
