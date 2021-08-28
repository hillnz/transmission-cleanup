# transmission-cleanup

A script to delete transmission files when free space falls below a threshold.

Connects to transmission to finds the oldest completed torrent, and then remove all its files (and any duplicate files).

## Environment Variables

Defaults are only set for the Dockerfile.

Name | Default | Description
--- | --- | ---
TRANSMISSION_HOST | | host:port for transmission
MIN_FREE | 53687091200 | Minimum free space required, else files will be deleted
CLEANUP_DIR | /cleanup | Directory that transmission downloads to
DELETE_TIME | 02:00 | (Docker only) Time of day to run
