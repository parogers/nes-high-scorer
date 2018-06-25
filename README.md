# NES High Scorer

Publishes high scores achieved in NES games.

This code is designed to work with a fork of libretro-fceu, the NES emulation
plugin for retroarch. The forked plugin is here:

https://github.com/parogers/libretro-fceumm

## How it works

The retroarch plugin is modified to create the NES RAM as a block of shared
memory, in the filesystem under '/dev/shm/fceu-shm'. This allows external
processes to directly read/write the contents of NES memory, letting us extract
things like high-scores.

An external python script periodically reads NES RAM and waits for the high
score table to be updated. The new score is then tweeted out.

## Tweeting high scores in Tetris

The script 'watch_for_high_scores.py' will wait until someone is playing
tetris, then monitor the high-score table for new high scores, and tweets
them out. See the script for details on how to get this running for yourself.
(you'll need to install python-twitter, obtain proper twitter credentials,
and copy + paste them into the right place -- see script for details)

## Utilities

## License

All source code is released under GPLv3 license. See file LICENSE for details.
