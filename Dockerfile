# syntax = docker/dockerfile:1.9
FROM python:3.12.5-slim AS base

ARG PIP_DISABLE_PIP_VERSION_CHECK=1
ARG PIP_NO_COMPILE=1
ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1
ENV PYTHON_PIP_VERSION=24.0.0
ENV PYTHON_SETUPTOOLS_VERSION=70.0.0

RUN python3 -m pip install -U pip=="${PYTHON_PIP_VERSION}" && \
    python3 -m pip install -U setuptools=="${PYTHON_SETUPTOOLS_VERSION}"

FROM base AS build-env

RUN python3 -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /

COPY ./requirements.txt ./

# Buildkits caching
RUN --mount=type=cache,target=/root/.cache/ \
      python3 -m pip install -r requirements.txt && \
      python3 -m pip install -U setuptools=="${PYTHON_SETUPTOOLS_VERSION}"

FROM base AS run

COPY --from=build-env /opt/venv /opt/venv

WORKDIR /app

COPY github_rate_limits_exporter/ ./github_rate_limits_exporter

RUN useradd -ms /bin/bash ubuntu

USER ubuntu

ENV PATH="/opt/venv/bin:$PATH"

EXPOSE 10050

ENTRYPOINT ["python", "-m", "github_rate_limits_exporter"]
