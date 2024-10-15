#!/usr/bin/env bash

# Processar argumentos do terminal
FORCE_REPLACE=false
while getopts "f" opt; do
    case $opt in
        f)
        FORCE_REPLACE=true
        ;;
        \?)
        echo "Invalid option: -$OPTARG" >&2
        exit 1
        ;;
    esac
done

PATH_UTILS=$HOME/.local/bin/pymodoro_utils
PATH_BIN=$HOME/.local/bin
PATH_DESKTOP=$HOME/.local/share/applications
PATH_ICON=$HOME/.local/share/icons
mkdir -p $PATH_UTILS
mkdir -p $PATH_BIN
mkdir -p $PATH_DESKTOP
mkdir -p $PATH_ICON
cp ../utils/pymodoro_darkmode.qss $PATH_UTILS
cp ../utils/pymodoro_lightmode.qss $PATH_UTILS
cp ../utils/pymodoro_icon.png $PATH_UTILS
cp ../utils/pymodoro_tray_icon.png $PATH_UTILS
cp ../utils/notification.wav $PATH_UTILS
cp bin/pymodoro $PATH_BIN
cp pymodoro.desktop $PATH_DESKTOP
cp ../utils/pymodoro_icon.png $PATH_ICON

if [ ! -f $PATH_UTILS/pymodoro_settings.json ] || [ "$FORCE_REPLACE" = true ]; then
    cp ../utils/pymodoro_settings.json $PATH_UTILS
fi