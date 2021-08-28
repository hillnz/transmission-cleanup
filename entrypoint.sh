#!/usr/bin/env bash

set -e

while true; do
    /cleanup.sh

    echo "Sleeping until tomorrow at ${DELETE_TIME}"
    sleep $(( $(date -d "tomorrow ${DELETE_TIME}" +%s) - $(date +%s) ))
done
