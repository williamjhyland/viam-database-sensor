#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Navigate to script directory
cd "$SCRIPT_DIR"

VENV_NAME="venv"
PYTHON="$VENV_NAME/bin/python"
ENV_ERROR="This module requires Python >=3.8, pip, and virtualenv to be installed."

# Function to check if all requirements are met
are_requirements_met() {
    local requirement
    while read -r requirement; do
        if ! $PYTHON -c "import pkg_resources; pkg_resources.require('$requirement')" 2>/dev/null; then
            return 1
        fi
    done < requirements.txt
    return 0
}
echo "Starting run script..."
# Create a virtual environment if it doesn't exist
if [ ! -d "$VENV_NAME" ]; then
    echo "Creating virtual environment..."

    # check for pip, virtualenv and venv
    if ! command -v pip3 >/dev/null; then
        echo "require python3-pip"
    fi
    
    if ! command -v virtualenv >/dev/null; then
        echo "require virtualenv"
    fi

    if ! command -v venv >/dev/null; then
        echo "require venv"
    fi
    # create virtual environment
    if ! python3 -m venv --system-site-packages "$VENV_NAME"; then
        echo "Failed to create virtualenv."
        exit 1
    fi
else
    echo "Virtual environment exists..."
fi

# Activate virtual environment
source "$VENV_NAME/bin/activate"

# Install/Upgrade Python packages if necessary
if ! are_requirements_met; then
    echo "Installing/upgrading Python packages..."
    if ! $PYTHON -m pip install -r requirements.txt -Uqq; then
        echo "Failed to install required packages."
        exit 1
    fi
else
    echo "All requirements are already met."
fi

echo "Starting module..."
exec ${PYTHON} ${SCRIPT_DIR}/src/main.py "$@"
