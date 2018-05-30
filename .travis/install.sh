#!/bin/bash

set -e
set -x

# See https://github.com/pyca/cryptography/blob/master/.travis/install.sh

if [[ $TRAVIS_OS_NAME == 'osx' ]]; then
    sw_vers

    # install pyenv
    git clone --depth 1 https://github.com/pyenv/pyenv ~/.pyenv
    PYENV_ROOT="$HOME/.pyenv"
    PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init -)"

    PYTHON_VER_LONG='error'
    PYTHON_VER_SHORT='error'
    case "${TOXENV}" in
        py36)
            PYTHON_VER_LONG='3.6.5'
            PYTHON_VER_SHORT='3.6'
            ;;
        py37)
            PYTHON_VER_LONG='3.7.15'
            PYTHON_VER_SHORT='3.7'
            ;;
    esac
    echo "Setting up Python ${PYTHON_VER_LONG}"
    pyenv install "${PYTHON_VER_LONG}"
    pyenv global "${PYTHON_VER_LONG}"
    pyenv rehash

    eval "python${PYTHON_VER_SHORT} -m venv ~/.travis-venv"
    source ~/.travis-venv/bin/activate

    pip3 install tox-pyenv
else
    # Install custom requirements on Linux
    pip3 install tox-travis
fi
