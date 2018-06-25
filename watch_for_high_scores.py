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
DELAY = 1

def get_config_dir():
    return os.path.join(os.getenv('HOME'), '.config', 'nes-high-scorer')

def read_secrets():
    path = os.path.join(get_config_dir(), 'secrets')
    return json.loads(open(path).read())

def post_tweet(msg):
    secrets = read_secrets()
    api = twitter.Api(
        consumer_key=secrets['consumer_key'],
        consumer_secret=secrets['consumer_secret'],
        access_token_key=secrets['access_token_key'],
        access_token_secret=secrets['access_token_secret'])
    api.VerifyCredentials()

    status = api.PostUpdate(msg)
    print(status, status.text)

def check_for_new_entries(old_entries, new_entries):
    ignored = (
        HighScoreEntry(1, 'A', 'HOWARD', 10000, 9),
        HighScoreEntry(2, 'A', 'OTASAN', 7500, 5),
        HighScoreEntry(3, 'A', 'LANCE', 5000, 0),
        HighScoreEntry(1, 'B', 'ALEX', 2000, 9),
        HighScoreEntry(2, 'B', 'TONY', 1000, 5),
        HighScoreEntry(3, 'B', 'NINTEN', 500, 0),
    )
    return [
        entry for entry in new_entries
        if entry not in old_entries and not entry in ignored]

def make_tweet(entry):
    # Fix the name by stripping off trailing dashes (default when you
    # enter a high-score)
    name = entry.name
    while name and name.endswith('-'):
        name = name[:-1]
    
    # bytes([0xF0, 0x9F, 0x8E, 0x86])
    fmt = 'Congrats {}!!! You scored {:,} pts and reached L{} ({}-type)'
    return fmt.format(
        name, entry.score, entry.level, entry.game_type)

# Santiy check for secrets
read_secrets()

# Periodically read NES memory to get a list of high scores. We tweet
# out a new high score whenever it appears in the list.
last_entries = []
while True:
    # Make sure tetris is being played
    if not nes.fceu.is_tetris_running():
        time.sleep(DELAY)
        continue
    
    try:
        ram = nes.fceu.open_shm()
        entries = nes.tetris.get_high_scores(ram)
        
    except FileNotFoundError:
        # The emulator isn't running apparently
        pass
    else:
        new_entries = check_for_new_entries(last_entries, entries)
        if new_entries and last_entries:
            # The high-score table has changed. We need to wait until the
            # player has finished entering their score (since it will change
            # on every letter they enter). This happens by watching the
            # play-field area of memory. It gets filled with horizontal
            # bars on game over (0x4f) then cleared again after the high-score
            # is entered (0xef)
            while ram[0x400] != 0xef:
                time.sleep(0.1)

            # Now we can fetch the proper entries
            entries = nes.tetris.get_high_scores(ram)
            new_entries = check_for_new_entries(last_entries, entries)

            print('*** New high scores:')
            for entry in new_entries:
                msg = make_tweet(entry)
                print(msg)
                post_tweet(msg)

            print('')

        last_entries = entries

    # Some throttling is needed
    time.sleep(DELAY)
