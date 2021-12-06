#!/usr/bin/env python3

import os
import sys

from subprocess import PIPE, run
from time import sleep

from transmission_rpc import Client


CLEANUP_DIR = os.environ['CLEANUP_DIR']
TRANSMISSION_HOST = os.environ['TRANSMISSION_HOST']
MIN_FREE = int(os.environ['MIN_FREE'])


def exec(*args: str):
    result = run(list(args), stdout=PIPE, check=True)
    return result.stdout.decode()

        
def torrent_for_file(transmission_client: Client, file_path: str):
    torrent_list = transmission_client.get_torrents()
    for t in torrent_list:
        for f in t.files():
            if f.name == file_path:
                return t


def main():
    transmission = Client(host=TRANSMISSION_HOST)

    while True:
        sleep(1)

        free_space = int(exec('findmnt', '-f', '-o', 'AVAIL', '-b', '-n', '-T', CLEANUP_DIR))
        if free_space >= MIN_FREE:
            print(f"Free space is {free_space}, no further cleanup required")
            break
        
        print(f"Free space ({free_space}) < minimum required ({MIN_FREE})")

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

            if empty and dir != CLEANUP_DIR:
                print(f'Removing empty dir {dir}')
                os.removedirs(dir)

        if oldest_file:
                 
            t = torrent_for_file(transmission, oldest_file)
            if t:
                print(f'Deleting torrent "{t.name}" and its files')
                transmission.remove_torrent(t.id, delete_data=True)
            else:
                print(f'Deleting file "{oldest_file}"')
                os.remove(oldest_file)

        else:
            print('The directory is already empty')
            break

if __name__ == '__main__':
    main()
