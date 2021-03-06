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
HighScoreEntry = namedtuple(
    'HighScoreEntry', ('rank', 'game_type', 'name', 'score', 'level'))

HIGH_SCORES_A = (
    HighScoreEntry(1, 'A', 0x700, 0x730, 0x748),
    HighScoreEntry(2, 'A', 0x706, 0x733, 0x749),
    HighScoreEntry(3, 'A', 0x70c, 0x736, 0x74a),
)

HIGH_SCORES_B = (
    HighScoreEntry(1, 'B', 0x718, 0x73c, 0x74c),
    HighScoreEntry(2, 'B', 0x71e, 0x73f, 0x74d),
    HighScoreEntry(3, 'B', 0x724, 0x742, 0x74e),
)

DEFAULT_HIGH_SCORES = (
    HighScoreEntry(1, 'A', 'HOWARD', 10000, 9),
    HighScoreEntry(2, 'A', 'OTASAN', 7500, 5),
    HighScoreEntry(3, 'A', 'LANCE ', 5000, 0),
    HighScoreEntry(1, 'B', 'ALEX  ', 2000, 9),
    HighScoreEntry(2, 'B', 'TONY  ', 1000, 5),
    HighScoreEntry(3, 'B', 'NINTEN', 500, 0),
)

VERTICAL_POS = 0x61
NEXT_PIECE = 0x62
CURRENT_PIECE = 0xbf

LINE_PIECE = 18

HIGH_SCORES_START = 0x700
HIGH_SCORES_END = 0x74e

CURRENT_SCORE_START = 0x73
CURRENT_SCORE_BYTES = 3

PLAY_AREA_START = 0x400
PLAY_AREA_BYTES = 200
PLAY_AREA_ROWS = 20
PLAY_AREA_COLS = 10

PLAY_AREA_BAR_FILL = 0x4f
PLAY_AREA_EMPTY = 0xef
PLAY_AREA_WHITE = 0x7b
PLAY_AREA_CYAN = 0x7c
PLAY_AREA_BLUE = 0x7d

def get_high_scores_by_table(ram, table, game_type):
    lst = []
    for count, entry in enumerate(table):
        name = ram[entry.name:entry.name+6]
        score = ram[entry.score:entry.score+3]
        level = ram[entry.level]

        if name[0] == 0xff:
            # RAM hasn't been initalized yet
            return None

        name = "".join(byte_to_char(ch) for ch in name)
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

def get_current_score_bytes(ram):
    return (ram[CURRENT_SCORE_START],
            ram[CURRENT_SCORE_START+1],
            ram[CURRENT_SCORE_START+2])

def get_current_score(ram):
    '''Returns the score of the game currently being played'''
    #lst = ram[CURRENT_SCORE_START:CURRENT_SCORE_START+CURRENT_SCORE_BYTES]
    lst = get_current_score_bytes(ram)
    return int(''.join('%02x' % n for n in reversed(lst)))
