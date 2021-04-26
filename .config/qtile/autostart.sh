#!/bin/bash
# Stuff to be run at startup.

nitrogen --restore &
picom --experimental-backends &
volumeicon &
nm-applet &
conky -c ~/.conkyrc &

