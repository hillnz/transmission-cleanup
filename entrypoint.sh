#!/usr/bin/env bash

set -e

while true; do
    /cleanup.py

    echo "Sleeping for half an hour..."
    sleep 30m
done
