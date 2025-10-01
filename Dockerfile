FROM python:3.12-slim

COPY ermd /tmp/app/ermd
COPY pyproject.toml /tmp/app/

RUN apt update -y

RUN pip install --break-system-packages --upgrade --no-cache-dir /tmp/app

RUN groupadd ermd && useradd --gid ermd ermd -md /app
USER ermd

WORKDIR /app

CMD ["ermd", "--host", "0.0.0.0", "--port", "8080", "--workers", "4", "--limit-concurrency", "100", "--limit-max-requests", "500"]
