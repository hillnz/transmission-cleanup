# transmission-cleanup

Deletes files from a directory to meet a disk free space threshold, oldest first. Connects to transmission to delete the associated downloaded torrent if it exists.

## Environment Variables

Defaults are only set for the Dockerfile.

Name | Default | Description
--- | --- | ---
TRANSMISSION_HOST | | host:port for transmission
MIN_FREE | 53687091200 | Minimum free space required, else files will be deleted
CLEANUP_DIR | /cleanup | Directory that transmission downloads to
DELETE_FREQ | | (Docker only) Frequency of run (e.g. 30m).
