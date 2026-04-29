FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        git \
        libxml2-dev \
        libxslt1-dev \
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
RUN pip install --no-deps -e .

CMD ["python", "-m", "unittest", "discover", "-s", "tests", "-v"]
