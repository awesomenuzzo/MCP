#!/bin/bash

# Define paths
UV_PATH="/Users/awesomenuzzo/.pyenv/shims/uv"
PROJECT_PATH="/Users/awesomenuzzo/Documents/Projects/SVHub/MCPServers/mcp-gsuite-main"
VENV_PATH="$PROJECT_PATH/.venv"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_PATH" ]; then
    mkdir -p "$VENV_PATH"
    $UV_PATH venv "$VENV_PATH"
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Install the package in development mode
cd "$PROJECT_PATH"
$UV_PATH pip install -e .

# Run the module using the entry point script
$UV_PATH run mcp-gsuite