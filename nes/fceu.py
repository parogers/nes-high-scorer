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

import mmap
import psutil
import re
import os

DEFAULT_SHM_PATH = '/dev/shm/fceu-shm'

def open_shm(path=DEFAULT_SHM_PATH):
    with open(path, 'r+b') as file:
        return mmap.mmap(file.fileno(), 0)

def is_shm_available(path=DEFAULT_SHM_PATH):
    return os.path.exists(path)

def get_proc():
    for proc in psutil.process_iter():
        if 'retroarch' in proc.name().lower():
            return proc
    return None

def is_tetris_running():
    """Make a reasonable guess as to whether tetris is being played"""
    # TODO - a bit of a hack
    proc = get_proc()
    return proc and any(
        re.match('.*tetris.*nes', arg.lower()) for arg in proc.cmdline())

