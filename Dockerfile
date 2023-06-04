# syntax = docker/dockerfile:1.3
FROM python:3.11.3-slim AS build

RUN python3 -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

# Requirements in separate stage
FROM build as build-env

WORKDIR /

COPY ./requirements.txt ./

ARG PIP_DISABLE_PIP_VERSION_CHECK=1
ARG PIP_NO_COMPILE=1
ENV PYTHON_PIP_VERSION=22.3.1
ENV PYTHON_SETUPTOOLS_VERSION=65.5.1

# Buildkits caching
RUN --mount=type=cache,target=/root/.cache/ \
      python3 -m pip install -U pip==${PYTHON_PIP_VERSION} && \
      python3 -m pip install -U setuptools==${PYTHON_SETUPTOOLS_VERSION} && \
      python3 -m pip install -r requirements.txt

FROM python:3.11.2-slim AS run

COPY --from=build-env /opt/venv /opt/venv

# CVE-2022-29458
# CVE-2023-0464
RUN apt-get update && \
      apt-get install -y \
      --only-upgrade \
      --no-install-recommends \
      libncursesw6=6.2+20201114-2+deb11u1 \
      ncurses-base=6.2+20201114-2+deb11u1 \
      ncurses-bin=6.2+20201114-2+deb11u1 \
      libssl1.1=1.1.1n-0+deb11u5 \
      openssl=1.1.1n-0+deb11u5 && \
      rm -rf /var/lib/apt/lists/* /var/cache/apt/*

WORKDIR /app

COPY github_rate_limits_exporter/ ./github_rate_limits_exporter

RUN useradd -ms /bin/bash ubuntu

USER ubuntu

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONFAULTHANDLER 1
ENV PYTHONUNBUFFERED=1

EXPOSE 10050

ENTRYPOINT ["python", "-m", "github_rate_limits_exporter"]
