# syntax=docker/dockerfile:1
FROM python:3.12-slim

ARG LAST_COMMIT
ENV DJANGO_PORT=8000 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LAST_COMMIT=$LAST_COMMIT \
    PATH="/app/scripts:${PATH}"

WORKDIR /app

COPY requirements.txt /app/
COPY requirements-dev.txt /app/

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        binutils \
        gcc \
        libpq-dev \
        python3-dev \
        gettext \
    ; \
    useradd -c "App User" \
        --home-dir /app \
        --shell /bin/sh \
        --create-home \
        --uid 1000 \
        app \
    ; \
    pip install --no-cache-dir --upgrade pip; \
    pip install --no-cache-dir --upgrade setuptools; \
    pip install --no-cache-dir -r requirements.txt; \
    pip install --no-cache-dir -r requirements-dev.txt; \
    mkdir -p /vol/web/static; \
    chown -R app:app /app; \
    chown -R app:app /vol/web; \
    apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false; \
    rm -rf /var/lib/apt/lists/*

COPY . /app/

USER 1000

VOLUME /var/web

EXPOSE $DJANGO_PORT
CMD ["entrypoint.sh"]