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

from . import fceu
from collections import namedtuple

LETTER_MAP = '-ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,/()\". '

def byte_to_char(ch):
    try:
        return LETTER_MAP[ch]
    except IndexError:
        return ' '

# TODO - this is a bit ugly
high_score_entry = namedtuple(
    'HighScoreEntry', ('rank', 'game_type', 'name', 'score', 'level'))

class HighScoreEntry(high_score_entry):
    # We don't want to include ranking in the equality test (since scores
    # can move around in ranking, but they are the same score)
    def __eq__(self, other):
        return (self.name == other.name and
                self.score == other.score and
                self.level == other.level and
                self.game_type == other.game_type)
        

HIGH_SCORES_A = (
    HighScoreEntry(1, 'A', 0x700, 0x730, 0x748),
    HighScoreEntry(2, 'A', 0x706, 0x733, 0x749),
    HighScoreEntry(3, 'A', 0x70c, 0x736, 0x74a),
)

HIGH_SCORES_B = (
    HighScoreEntry(1, 'B', 0x718, 0x73c, 0x74c),
    HighScoreEntry(2, 'B', 0x71d, 0x73f, 0x74d),
    HighScoreEntry(3, 'B', 0x724, 0x742, 0x74e),
)

VERTICAL_POS = 0x61
NEXT_PIECE = 0x62
CURRENT_PIECE = 0xbf

LINE_PIECE = 18

HIGH_SCORES_START = 0x700
HIGH_SCORES_END = 0x74e

def get_high_scores_by_table(ram, table, game_type):
    lst = []
    for count, entry in enumerate(table):
        name = ram[entry.name:entry.name+6]
        score = ram[entry.score:entry.score+3]
        level = ram[entry.level]

        if name[0] == 0xff:
            # RAM hasn't been initalized yet
            return None

        name = "".join(byte_to_char(ch) for ch in name).strip()
        # Note: the score is BCD encoded
        try:
            score = int("".join('%02x' % ch for ch in score))
        except:
            # If the score isn't valid, the table probably isn't valid
            return None

        lst.append(HighScoreEntry(count+1, game_type, name, score, level))
    return lst

def get_high_scores(ram):
    """Extracts and returns the high scores from the given block of RAM."""
    a_list = get_high_scores_by_table(ram, HIGH_SCORES_A, 'A')
    if not a_list:
        return None
    b_list = get_high_scores_by_table(ram, HIGH_SCORES_B, 'B')
    if not b_list:
        return None
    return a_list + b_list

if __name__ == '__main__':
    ram = fceu.open_shm()
    for entry in get_high_scores(ram):
        print(entry.name, entry.score, entry.level)

