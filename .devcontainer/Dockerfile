FROM public.ecr.aws/docker/library/python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV COLUMNS=200

# Install system dependencies and dev tools
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    build-essential \
    git \
    curl \
    vim \
    less \
    iputils-ping \
    net-tools \
    htop \
    unzip \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir uv

# Set the working directory
WORKDIR /workspace

# (Do not copy code here; mounting source for dev)

# Install Python dependencies if needed
COPY ../pyproject.toml ../uv.lock ./
RUN uv export --format requirements-txt --no-dev > requirements.txt && uv pip install --system -r requirements.txt || true

# Set Python path
ENV PYTHONPATH=/workspace

# Default command
CMD ["bash"]

# Create vscode user for VS Code Dev Containers compatibility
RUN useradd -m vscode \
    && echo "vscode ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/vscode \
    && chmod 0440 /etc/sudoers.d/vscode

USER vscode
