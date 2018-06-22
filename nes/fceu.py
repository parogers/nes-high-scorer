
import mmap

DEFAULT_SHM_PATH = '/dev/shm/fceu-shm'

def open_shm(path=DEFAULT_SHM_PATH):
    with open(path, 'r+b') as file:
        return mmap.mmap(file.fileno(), 0)
