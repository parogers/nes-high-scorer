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

