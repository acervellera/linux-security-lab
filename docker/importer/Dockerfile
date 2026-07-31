FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN groupadd --system --gid 10001 importer \
    && useradd --system --uid 10001 --gid importer --no-create-home importer

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN python -m pip install \
        --no-cache-dir \
        --no-compile \
        -r /app/requirements.txt

COPY --chown=10001:10001 --chmod=0555 importer.py /app/importer.py

USER 10001:10001

ENTRYPOINT ["python", "/app/importer.py"]
