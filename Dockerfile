# syntax = docker/dockerfile:1.3
FROM python:3.12.3-slim AS build

RUN python3 -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

# Requirements in separate stage
FROM build as build-env

WORKDIR /

COPY ./requirements.txt ./

ARG PIP_DISABLE_PIP_VERSION_CHECK=1
ARG PIP_NO_COMPILE=1
ENV PYTHON_PIP_VERSION=23.1.2
ENV PYTHON_SETUPTOOLS_VERSION=68.0.0

# Buildkits caching
RUN --mount=type=cache,target=/root/.cache/ \
      python3 -m pip install -U pip==${PYTHON_PIP_VERSION} && \
      python3 -m pip install -U setuptools==${PYTHON_SETUPTOOLS_VERSION} && \
      python3 -m pip install -r requirements.txt

FROM python:3.12.3-slim AS run

RUN apt-get update && \
    apt-get install -y \
    --only-upgrade \
    --no-install-recommends \
    libc-bin=2.36-9+deb12u7 && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/*

COPY --from=build-env /opt/venv /opt/venv

WORKDIR /app

COPY github_rate_limits_exporter/ ./github_rate_limits_exporter

RUN useradd -ms /bin/bash ubuntu

USER ubuntu

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONFAULTHANDLER 1
ENV PYTHONUNBUFFERED=1

EXPOSE 10050

ENTRYPOINT ["python", "-m", "github_rate_limits_exporter"]
