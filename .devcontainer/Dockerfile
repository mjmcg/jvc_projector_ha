FROM mcr.microsoft.com/devcontainers/python:3.12

# Prevent Python from writing pyc files everywhere
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Home Assistant expects certain system deps
RUN apt-get update && apt-get install -y \
    libffi-dev \
    libssl-dev \
    libjpeg-dev \
    zlib1g-dev \
    libopenjp2-7 \
    libturbojpeg0 \
    ffmpeg \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip + install HA dev tooling
RUN pip install --upgrade pip \
    && pip install \
        homeassistant \
        pytest \
        pytest-cov \
        ruff \
        mypy \
        types-PyYAML

# Create expected HA config directory
RUN mkdir -p /home/vscode/.homeassistant \
    && chown -R vscode:vscode /home/vscode/.homeassistant

WORKDIR /workspace