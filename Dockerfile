FROM --platform=linux/amd64 python:3.12-slim

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    openssh-client \
    zip \
    libxml2-dev \
    libxslt-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN cp config.ini-TEMPLATE config.ini

# Diretórios necessários em tempo de execução
RUN mkdir -p /var/log/processing /root/.ssh

# Aceita automaticamente novos hosts SSH (evita prompt interativo no SCP)
RUN echo "StrictHostKeyChecking accept-new" >> /etc/ssh/ssh_config

# Variáveis de ambiente para modo Docker (sem virtualenv)
# PROCESSING_SETTINGS_FILE aponta para o template por padrão;
# em produção, montar o arquivo real via -v /etc/scieloapps/processing.ini:...
ENV PROCESSING_SETTINGS_FILE=/app/config.ini
ENV DOCKER_ENV=1
ENV WORK_DIR=/app
ENV LOG_DIR=/var/log/processing
ENV PYTHONPATH=/app

RUN pip install --no-cache-dir pytest

# Install thriftpy2 (Python 3 fork of thriftpy) and create a proper thriftpy
# shim so that older packages (articlemetaapi, etc.) can still `import thriftpy`
RUN pip install --no-cache-dir thriftpy2 && python3 docker_thriftpy_shim.py

# Install git-based dependencies (non-editable)
RUN pip install --no-cache-dir \
    "git+https://github.com/fabiobatalha/doaj_client@27c2c17dc6d0d9ee3aa12283b20c1ac6170869b6" \
    "git+https://github.com/scieloorg/scieloh5m5.git@1.9.6" \
    "git+https://github.com/scieloorg/xylose.git@1.35.13"

# Install remaining dependencies from requirements.txt:
# - skip -e git lines (already handled above)
# - skip thriftpy lines (thriftpy2 + shim already installed)
# - unpin lxml (4.5.0 has no Python 3.12 wheel)
# - unpin requests/urllib3/certifi/chardet/idna (pinned versions incompatible with Python 3.12)
RUN grep -v "^-e " requirements.txt \
    | grep -v "^thriftpy" \
    | sed 's/^lxml==[0-9.]*/lxml/' \
    | sed 's/^requests==[0-9.]*/requests/' \
    | sed 's/^urllib3==[0-9.]*/urllib3/' \
    | sed 's/^certifi==[0-9.]*/certifi/' \
    | sed 's/^chardet==[0-9.]*/chardet/' \
    | sed 's/^idna==[0-9.]*/idna/' \
    | pip install --no-cache-dir -r /dev/stdin

RUN pip install --no-cache-dir -e .

RUN chmod +x run.sh

# Padrão: rodar o script de processamento
# Para rodar os testes: docker run --rm scielo-processing python -m pytest tests/ -v
ENTRYPOINT ["./run.sh"]
