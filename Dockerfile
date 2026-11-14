FROM python:3.13-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# PyPI has no armv7 wheel for cffi (needed by cryptography), so it is compiled here.
# Only PyPI is trusted as package source; the compiler stays out of the final image.
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libc6-dev libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip wheel --wheel-dir /wheels -r requirements.txt


FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    CONFIG_DIR=/config

WORKDIR /app
COPY requirements.txt ./
RUN --mount=type=bind,from=builder,source=/wheels,target=/wheels \
    pip install --no-index --find-links /wheels -r requirements.txt

COPY run.py ./
COPY src ./src

RUN useradd --system --uid 1000 --no-create-home app
USER app

# server_config.json, mqtt_config.json and token.json are mounted here at runtime,
# so no credentials are ever baked into the image
VOLUME ["/config"]

CMD ["python", "run.py"]
