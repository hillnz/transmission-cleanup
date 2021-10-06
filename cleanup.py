#!/usr/bin/env python3

import os
import sys

from dataclasses import dataclass
from subprocess import PIPE, run
from time import sleep
from typing import List


CLEANUP_DIR = os.environ['CLEANUP_DIR']
TRANSMISSION_HOST = os.environ['TRANSMISSION_HOST']
MIN_FREE = int(os.environ['MIN_FREE'])


@dataclass
class Torrent:
    id: str
    name: str
    files: List[str]


def exec(*args: str):
    result = run(list(args), stdout=PIPE, check=True)
    return result.stdout.decode()


def transmission(*args: str):
    return exec('transmission-remote', TRANSMISSION_HOST, *args)


def transmission_list():
    output = transmission('-l')
    lines = output.splitlines()
    for n, line in enumerate(lines):
        if n == 0 or n >= len(lines) - 2:
            continue
        fields = line.split()
        t = Torrent(
            id=fields[0],
            name=fields[9],
            files=[]
        )
        files = transmission(f'-t{t.id}', '--files').splitlines()
        t.files=[ f for n, f in enumerate(files) if n <= len(files) - 3 ]
        yield t


def torrent_for_file(torrent_list: List[Torrent], file_path: str):
    for t in torrent_list:
        for f in t.files:
            if f == file_path:
                return t


while True:
    sleep(1)

    free_space = int(exec('findmnt', '-f', '-o', 'AVAIL', '-b', '-n', '-T', CLEANUP_DIR))
    if free_space >= MIN_FREE:
        print(f"Free space is {free_space}, no further cleanup required")
        break
    
    print(f"Free space ({free_space}) < minimum required ({MIN_FREE})")
    
    torrents = list(transmission_list())

    oldest_mtime = sys.maxsize
    oldest_file = ''
    dirs = [CLEANUP_DIR]

    while len(dirs) > 0:
        dir = dirs.pop()
        
        empty = True
        for f in os.scandir(dir):
            empty = False
            
            if f.is_dir():
                dirs.append(f.path)
                continue
            
            modified = f.stat().st_mtime
            if modified < oldest_mtime:
                oldest_mtime = modified
                oldest_file = f.path

        if empty:
            print(f'Removing empty dir {dir}')
            os.removedirs(dir)

    if oldest_file:
        
        t = torrent_for_file(torrents, oldest_file)
        if t:
            print(f'Deleting torrent "{t.name}" and its files')
            transmission(f'-t{t.id}', '--remove-and-delete')
        else:
            print(f'Deleting file "{oldest_file}"')
            os.remove(oldest_file)

    else:
        print('The directory is already empty')
