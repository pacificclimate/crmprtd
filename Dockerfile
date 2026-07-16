# syntax=docker/dockerfile:1
#
# Container image for crmprtd, intended to be driven by Kestra (or any
# orchestrator) as a task runner. The image places every crmprtd console
# script on PATH so a task can invoke any sub-command, e.g.:
#
#   docker run --rm crmprtd crmprtd_pipeline --help
#   docker run --rm crmprtd crmprtd_download -N ec ...
#   docker run --rm crmprtd crmprtd_process ...
#
# Available entry points (see [project.scripts] in pyproject.toml):
#   crmprtd_pipeline  crmprtd_download  crmprtd_process
#   crmprtd_gulpy     bulk_pipeline     bulk_process
#
# A two-stage build keeps the runtime image free of compilers and *-dev
# headers: the builder compiles psycopg2/lxml and resolves the locked
# dependency set into an in-project virtualenv, which is copied into a slim
# runtime layer.

ARG PYTHON_VERSION=3.13
ARG POETRY_VERSION=2.1.3

########################################################################
# Builder: resolve and install dependencies into /app/.venv
########################################################################
FROM python:${PYTHON_VERSION}-slim AS builder

ARG POETRY_VERSION
ENV POETRY_VERSION=${POETRY_VERSION} \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

# Build-time system dependencies required to compile psycopg2 (libpq-dev)
# and lxml (libxml2-dev, libxslt1-dev).
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        libxml2-dev \
        libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"

WORKDIR /app

# Copy the metadata and sources Poetry needs to install the root package.
# The package source is required up front because Poetry installs the
# crmprtd project itself (not just its dependencies), and its data files
# (data/*.xsl, data/*.yaml, networks/*/*.yaml) are loaded at runtime via
# importlib.resources.files("crmprtd").
COPY pyproject.toml poetry.lock README.md ./
COPY crmprtd ./crmprtd

# Install runtime dependencies + optional extras (jsonlogger) into an
# in-project .venv, excluding dev/test tooling.
RUN poetry install --only main --all-extras

########################################################################
# Runtime: slim image carrying only the venv, sources, and shared libs
########################################################################
FROM python:${PYTHON_VERSION}-slim AS runtime

# Runtime shared libraries for the compiled wheels: libpq5 (psycopg2),
# libxml2 + libxslt1.1 (lxml). jq is included so tasks can query/shape the
# JSON logs and results the scripts emit (e.g. the "results" summary lines).
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq5 \
        libxml2 \
        libxslt1.1 \
        jq \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Bring over the resolved virtualenv and the package sources. The venv's
# console scripts and its editable install of crmprtd both reference
# /app/crmprtd, so the source tree must live at the same path.
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/crmprtd /app/crmprtd
COPY --from=builder /app/pyproject.toml /app/README.md /app/

# Run as an unprivileged user. /data is the recommended mount point for the
# shared working directory (raw cache + logs) used to hand data between the
# Download and Process tasks in a Swarm/Kestra deployment. Creating it owned by
# the runtime user means a fresh named volume mounted there inherits that
# ownership; bind/NFS mounts still take the host directory's ownership (see
# docs/installation/docker.md).
RUN useradd --create-home --uid 1000 crmprtd \
    && mkdir /data \
    && chown -R crmprtd:crmprtd /app /data
USER crmprtd

# No ENTRYPOINT: Kestra (or `docker run`) supplies the sub-command to run.
# The default just prints pipeline help so a bare `docker run` is useful.
CMD ["crmprtd_pipeline", "--help"]
