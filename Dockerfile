FROM python:3.12.2 AS reqs

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN /root/.poetry/bin/poetry export -o requirements.txt

FROM python:3.12.2-slim

ENV MIN_FREE=53687091200 \
    DELETE_FREQ=30m \
    CLEANUP_DIR=/cleanup \
    TRANSMISSION_HOST=

RUN apt-get update && apt-get install -y \
    transmission-cli

COPY --from=reqs /app/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt && rm /tmp/requirements.txt
COPY cleanup.py /
COPY entrypoint.sh /

ENTRYPOINT [ "/entrypoint.sh" ]
