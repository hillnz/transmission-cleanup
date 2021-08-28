#!/usr/bin/env bash

set -e

if [ -z "$CLEANUP_DIR" ]; then
    echo "CLEANUP_DIR is not set"
fi
if [ -z "$TRANSMISSION_HOST" ]; then
    echo "TRANSMISSION_HOST is not set"
fi
if [ -z "$MIN_FREE" ]; then
    echo "MIN_FREE is not set"
fi

transmission() {
    transmission-remote "$TRANSMISSION_HOST" "$@"
}

while true; do
    sleep 1

    free_space=$(findmnt -f -o AVAIL -b -n -T "$CLEANUP_DIR")
    if (( free_space >= MIN_FREE )); then
        echo "Free space is $free_space, no further cleanup required"
        break
    fi
    echo "Free space ($free_space) < minimum required ($MIN_FREE)"
    
    # Find the oldest completed torrent
    earliest_id=0
    earliest_date="9999-00-00T00:00:00+00:00"
    earliest_name=

    IFS=$'\n'
    for line in $(transmission -l | tail -n +2 | head -n -1); do
        tid="$(echo "$line" | awk '{print $1;}')"
        name="$(echo "$line" | awk '{print $10;}')"
        status="$(transmission "-t$tid" -i)"
        if ! echo "$status" | grep 'Percent Done: 100%' >/dev/null; then
            continue;
        fi
        date_finished_raw="$(echo "$status" | grep 'Date finished' | cut -c17-)"
        normalised_date="$(date -d "$date_finished_raw" -Iseconds)"
        if [[ "$normalised_date" < "$earliest_date" ]]; then
            earliest_date="$normalised_date"
            earliest_id="$tid"
            earliest_name="$name"
        fi
    done
    unset IFS

    if [ "$earliest_id" = 0 ]; then
        echo "WARNING: There are no torrents to delete despite the disk being low on space."
        break
    fi

    echo "The oldest torrent finished at $earliest_date and will be deleted: $earliest_id ($earliest_name)"
    
    # Locate duplicates to be deleted
    IFS=$'\n'
    for line in $(transmission "-t$earliest_id" --files | tail -n +3); do
        file="$CLEANUP_DIR/$(echo "$line" | awk '{print $7;}')"
        if [ ! -f "$file" ]; then
            echo "WARNING torrent file doesn't exist: $file"
            continue
        fi
        for other_file in "$CLEANUP_DIR"/**/*; do
            if [ -f "$other_file" ] && [ "$file" != "$other_file" ] && diff "$file" "$other_file" >/dev/null; then
                echo "Found a duplicate file to delete: $other_file"
                rm "$other_file"
            fi
        done
    done
    unset IFS

    transmission "-t$earliest_id" --remove-and-delete
done
