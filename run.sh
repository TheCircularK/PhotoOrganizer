#!/usr/bin/env bash
set -e

# Configuration
PYTHON_VERSION="3.14"
VENV_DIR=".venv"
REQUIREMENTS_FILE="requirements.txt"
APP_FILE="app.py"

# Helper function to print messages
log() {
    echo -e "\033[1;34m[INFO]\033[0m $1"
}

# 1. Check if python 3.14 is installed
if ! command -v python3 &>/dev/null || ! python3 --version | grep -q "$PYTHON_VERSION"; then
    log "Python $PYTHON_VERSION not found. Installing..."
    
    if [[ "$(uname)" == "Linux" ]]; then
        if command -v dnf &>/dev/null; then
            sudo dnf install -y "python${PYTHON_VERSION}" "python${PYTHON_VERSION}-venv" "python${PYTHON_VERSION}-devel"
        else
            log "DNF not found. Please install Python $PYTHON_VERSION manually."
            exit 1
        fi
    elif [[ "$(uname)" == "Darwin" ]]; then
        log "On macOS, install Python $PYTHON_VERSION via Homebrew:"
        log "brew install python@$PYTHON_VERSION"
        exit 1
    else
        log "Unsupported OS. Please install Python $PYTHON_VERSION manually."
        exit 1
    fi
else
    log "Python $PYTHON_VERSION is already installed."
fi

# 2. Check if tkinter is installed for this python
if ! python3 -c "import tkinter" &>/dev/null; then
    log "Tkinter not found. Installing..."
    sudo dnf install -y "python${PYTHON_VERSION}-tkinter"
else
    log "Tkinter is already installed."
fi

# 3. Check if venv exists
if [[ ! -d "$VENV_DIR" ]]; then
    log "Creating virtual environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
else
    log "Virtual environment already exists."
fi

# 4. Activate virtual environment
log "Activating virtual environment..."
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

# 5. Install requirements if needed
if [[ -f "$REQUIREMENTS_FILE" ]]; then
    log "Installing requirements from $REQUIREMENTS_FILE..."
    pip install --upgrade pip
    pip install -r "$REQUIREMENTS_FILE"
else
    log "No requirements.txt found, skipping."
fi

# 6. Run the app
if [[ -f "$APP_FILE" ]]; then
    log "Running $APP_FILE..."
    python "$APP_FILE"
else
    log "Error: $APP_FILE not found."
    exit 1
fi
