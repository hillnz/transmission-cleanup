#!/usr/bin/env bash

set -e

while true; do
    /cleanup.py

    echo "Sleeping for $DELETE_FREQ..."
    sleep "$DELETE_FREQ"
done
