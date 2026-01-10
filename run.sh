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
if ! command -v "python${PYTHON_VERSION}" &>/dev/null; then
    log "Python $PYTHON_VERSION not found. Installing..."
    
    if command -v dnf &>/dev/null; then
        sudo dnf install -y "python${PYTHON_VERSION}" "python${PYTHON_VERSION}-tools" --skip-broken --skip-unavailable
    else
        log "DNF not found. Please install Python $PYTHON_VERSION manually."
        exit 1
    fi
else
    log "Python $PYTHON_VERSION is already installed."
fi

# 2. Ensure tkinter works
if ! "python${PYTHON_VERSION}" -c "import tkinter" &>/dev/null; then
    log "Tkinter not found. Installing..."
    sudo dnf install -y python3-tkinter --skip-broken --skip-unavailable
else
    log "Tkinter is already installed."
fi

# 3. Check if venv exists
if [[ ! -d "$VENV_DIR" ]]; then
    log "Creating virtual environment in $VENV_DIR..."
    "python${PYTHON_VERSION}" -m venv "$VENV_DIR"
else
    log "Virtual environment already exists."
fi

# 4. Activate virtual environment
log "Activating virtual environment..."
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

# 5. Upgrade pip and install requirements
log "Upgrading pip..."
python -m pip install --upgrade pip

if [[ -f "$REQUIREMENTS_FILE" ]]; then
    log "Installing requirements from $REQUIREMENTS_FILE..."
    python -m pip install -r "$REQUIREMENTS_FILE"
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
