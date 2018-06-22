# NES High Scorer

Publishes high scores achieved in NES games.

This code is designed to work with a fork of libretro-fceu, the NES emulation
plugin for retroarch. The forked plugin is here:

https://github.com/parogers/libretro-fceumm

# How it works

The retroarch plugin is modified to create the NES RAM as a block of shared
memory, in the filesystem under '/dev/shm/fceu-shm'. This allows external
processes to directly read/write the contents of NES memory, letting us extract
things like high-scores.

An external python script periodically reads NES RAM and waits for the high
score table to be updated. The new score is then tweeted out.

## License

All source code is released under GPLv3 license. See file LICENSE for details.
