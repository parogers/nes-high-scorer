#!/usr/bin/env python3

import twitter
import json
import os
import nes, nes.fceu, nes.tetris
import time

from nes.tetris import HighScoreEntry

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

    print(api.VerifyCredentials())

    #status = api.PostUpdate('Hello, World!')
    #print(status, status.text)

def read_high_scores_from_ram():
    ram = nes.fceu.open_shm()
    return nes.tetris.get_high_scores(ram)

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

# Periodically read NES memory to get a list of high scores. We tweet
# out a new high score whenever it appears in the list.
last_entries = []
while True:
    # Make sure tetris is being played
    if not nes.fceu.is_tetris_running():
        time.sleep(10)
        continue
    
    try:
        entries = read_high_scores_from_ram()
    except FileNotFoundError:
        # The emulator isn't running apparently
        pass
    else:
        new_entries = check_for_new_entries(last_entries, entries)
        if new_entries:
            print('New high scores:')
            for entry in new_entries:
                print(entry.game_type, entry.name,
                      entry.level, entry.score)
            print('')

        last_entries = entries

    # Some throttling is needed
    time.sleep(10)
