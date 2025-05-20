# Use an official Python runtime as a parent image
FROM python:3.9-slim

LABEL maintainer="Your Name <your.email@example.com>"
LABEL description="Claude-powered CLI coding agent for Python development"
LABEL version="1.0"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1

# Set the working directory in the container for app files
WORKDIR /app

# Install dependencies
# Copy only requirements.txt first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip cache purge

# Copy the rest of the application code into the container
# This includes agent/, run.py, etc.
COPY . .

# Create a /workspace directory that can be used as a volume
# The agent is expected to operate on files within this workspace.
RUN mkdir -p /workspace && \
    chmod +x run.py

# Set the workspace as a volume to allow mounting from host
VOLUME /workspace

# Set the default working directory for the command execution to /workspace
# This means when run.py starts, its CWD will be /workspace.
# Tools using relative paths (like list_files default) will operate on /workspace.
WORKDIR /workspace

# Expose any ports if needed (currently no server functionality, but for future)
# EXPOSE 8000

# Command to run the application
# The application code (run.py) is in /app.
CMD ["python", "/app/run.py"]