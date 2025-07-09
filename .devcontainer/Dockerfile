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
    sudo \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir uv

# Create vscode user
RUN groupadd --gid 1000 vscode \
    && useradd --uid 1000 --gid vscode --shell /bin/bash --create-home vscode \
    && echo vscode ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/vscode \
    && chmod 0440 /etc/sudoers.d/vscode

# Set the working directory
WORKDIR /workspace

# Install Python dependencies if needed (as root before switching user)
COPY ../pyproject.toml ../uv.lock ./
RUN uv export --format requirements-txt --no-dev > requirements.txt && uv pip install --system -r requirements.txt || true

# Change ownership of workspace to vscode user
RUN chown -R vscode:vscode /workspace

# Switch to vscode user
USER vscode

# Set Python path
ENV PYTHONPATH=/workspace

# Default command
CMD ["bash"]
