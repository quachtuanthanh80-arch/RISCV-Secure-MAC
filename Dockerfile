# ==============================================================================
# Dockerfile for RISCV-Secure-MAC Artifact Evaluation & Verification Environment
# Reproducible IEEE/ACM Hardware Verification Container
# ==============================================================================
FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies, C++ compiler, Icarus Verilog, and Python 3
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    make \
    git \
    iverilog \
    python3 \
    python3-pip \
    python3-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Install Python packages required for Cocotb simulation and PySlang AST analysis
RUN pip3 install --no-cache-dir \
    cocotb==2.1.0 \
    cocotb-tools \
    pyslang \
    matplotlib \
    pytest

# Copy repository source code
COPY . /workspace

# Set default command to run all 18 master verification suites
CMD ["python3", "run_all_tests.py"]
