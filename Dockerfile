FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PROCESSING_SETTINGS_FILE=/app/config.ini \
    DOCKER_ENV=1 \
    WORK_DIR=/app \
    LOG_DIR=/var/log/processing \
    TABS_DIR=/var/www/static_scielo_org/tabs \
    PYTHONPATH=/app

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        libxml2-dev \
        libxslt1-dev \
        zip \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt setup.py ./
RUN pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt \
    && pip install --no-deps \
        accessstatsapi==1.2.1 \
        articlemetaapi==1.26.7 \
        citedbyapi==1.11.3 \
        publicationstatsapi==1.2.2 \
        packtools==2.6.4

COPY . .
RUN cp config.ini-TEMPLATE config.ini \
    && mkdir -p /var/log/processing /var/www/static_scielo_org/tabs \
    && pip install --no-deps -e .

ENTRYPOINT ["/bin/bash", "/app/run.sh"]
