FROM python:3.9.7-slim

ENV MIN_FREE=53687091200 \
    DELETE_TIME=02:00 \
    CLEANUP_DIR=/cleanup \
    TRANSMISSION_HOST=

RUN apt-get update && apt-get install -y \
    transmission-cli

COPY cleanup.py /
COPY entrypoint.sh /

ENTRYPOINT [ "/entrypoint.sh" ]
