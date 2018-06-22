#!/usr/bin/env python3

import fceu
from collections import namedtuple

LETTER_MAP = '-ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,/()\". '

def byte_to_char(ch):
    try:
        return LETTER_MAP[ch]
    except IndexError:
        return ' '

HighScoreEntry = namedtuple('HighScoreEntry', ('name', 'score', 'level'))

HIGH_SCORES_A = (
    HighScoreEntry(0x700, 0x730, 0x748),
    HighScoreEntry(0x706, 0x733, 0x749),
    HighScoreEntry(0x70c, 0x736, 0x74a),
)

HIGH_SCORES_B = (
    HighScoreEntry(0x718, 0x73c, 0x74c),
    HighScoreEntry(0x71d, 0x73f, 0x74d),
    HighScoreEntry(0x724, 0x742, 0x74e),
)

def get_high_scores_by_table(ram, table):
    lst = []
    for entry in table:
        name = ram[entry.name:entry.name+6]
        score = ram[entry.score:entry.score+3]
        level = ram[entry.level]

        name = "".join(byte_to_char(ch) for ch in name).strip()
        # Note: the score is BCD encoded
        score = int("".join('%02x' % ch for ch in score))
        lst.append(HighScoreEntry(name, score, level))
    return lst

def get_high_scores(ram):
    """Extracts and returns the high scores from the given block of RAM. 
    This returns a 2-tuple of two lists: A-type, and B-type scores. Each
    entry in thoses lists are HighScoreEntry types."""
    return (
        get_high_scores_by_table(ram, HIGH_SCORES_A),
        get_high_scores_by_table(ram, HIGH_SCORES_B))

if __name__ == '__main__':
    ram = fceu.open_shm()
    a_type, b_type = get_high_scores(ram)
    for entry in a_type + b_type:
        print(entry.name, entry.score, entry.level)

