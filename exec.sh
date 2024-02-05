#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Create virtual Python environment
cd `dirname $0`

# Create a virtual environment to run our code
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


# install pip and virtualenv if not installed
if ! command -v pip3 >/dev/null; then
    sudo apt install -qqy python3-pip
fi

if ! command -v virtualenv >/dev/null; then
    sudo pip3 install virtualenv
fi


if ! python3 -m venv --system-site-packages $VENV_NAME >/dev/null 2>&1; then
    echo "Failed to create virtualenv."
    if command -v apt-get >/dev/null; then
        echo "Detected Debian/Ubuntu, attempting to install python3-venv automatically."
        SUDO="sudo"
        if ! command -v $SUDO >/dev/null; then
            SUDO=""
        fi
		if ! apt info python3-venv >/dev/null 2>&1; then
			echo "Package info not found, trying apt update"
			$SUDO apt -qq update >/dev/null
		fi
        $SUDO apt install -qqy python3-venv >/dev/null 2>&1
        if ! python3 -m venv $VENV_NAME >/dev/null 2>&1; then
            echo $ENV_ERROR >&2
            exit 1
        fi
    else
        echo $ENV_ERROR >&2
        exit 1
    fi
fi

echo "Virtualenv found/created. Installing/upgrading Python packages..."
if ! $PYTHON -m pip install -r requirements.txt -Uqq; then
    exit 1
fi

echo "Starting module..."
exec ${SCRIPT_DIR}/venv/bin/python3 ${SCRIPT_DIR}/src/main.py $@