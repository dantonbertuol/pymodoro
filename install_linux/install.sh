#!/usr/bin/env bash
PATH_UTILS=$HOME/.local/bin/pymodoro_utils
PATH_BIN=$HOME/.local/bin
PATH_DESKTOP=$HOME/.local/share/applications
PATH_ICON=$HOME/.local/share/icons
mkdir -p $PATH_UTILS
mkdir -p $PATH_BIN
mkdir -p $PATH_DESKTOP
mkdir -p $PATH_ICON
cp ../utils/pymodoro_darkmode.qss $PATH_UTILS
cp ../utils/pymodoro_icon.png $PATH_UTILS
cp ../utils/notification.wav $PATH_UTILS
cp bin/pymodoro $PATH_BIN
cp pymodoro.desktop $PATH_DESKTOP
cp ../utils/pymodoro_icon.png $PATH_ICON