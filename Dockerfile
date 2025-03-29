# syntax = docker/dockerfile:1.9
FROM python:3.13.2-slim AS base

# CVE-2024-454[90-91-92]
RUN apt-get update && \
    apt-get install -y \
    --no-install-recommends \
    libexpat1=2.5.0-1+deb12u1 \
    libsqlite3-0=3.40.1-2+deb12u1 && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/*

ARG PIP_DISABLE_PIP_VERSION_CHECK=1
ARG PIP_NO_COMPILE=1
ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1
ENV PYTHON_PIP_VERSION=24.0.0

RUN python3 -m pip install -U pip=="${PYTHON_PIP_VERSION}"

FROM base AS build-env

RUN python3 -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /

COPY ./requirements.txt ./

# Buildkits caching
RUN --mount=type=cache,target=/root/.cache/ \
      python3 -m pip install -r requirements.txt

FROM base AS run

COPY --from=build-env /opt/venv /opt/venv

WORKDIR /app

COPY github_rate_limits_exporter/ ./github_rate_limits_exporter

RUN useradd -ms /bin/bash ubuntu

USER ubuntu

ENV PATH="/opt/venv/bin:$PATH"

EXPOSE 10050

ENTRYPOINT ["python", "-m", "github_rate_limits_exporter"]
