#!/usr/bin/env bash
python3 -m venv ../.env
source ../.env/bin/activate
pip install -r ../requirements.txt
pyinstaller -F --icon ../utils/pymodoro_icon.png ../pymodoro.py
mv dist/pymodoro bin
rm -rf build dist pymodoro.spec