# Base image
FROM ubuntu:20.04

# Prevent tzdata from prompting during install
ENV DEBIAN_FRONTEND=noninteractive

# System dependencies
RUN apt-get update && apt-get install -y \
    python3.8 \
    python3.8-dev \
    python3.8-tk \
    python3-pip \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Make python3.8 the default python
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.8 1

# Upgrade pip
RUN python -m pip install --upgrade pip

# Install Python dependencies
RUN pip install \
    otree==5.7.2

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Expose oTree default port
EXPOSE 8000

# Default command
CMD ["otree", "devserver", "0.0.0.0:8000"]
