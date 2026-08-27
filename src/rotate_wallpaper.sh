#!/usr/bin/env bash
# rotate_wallpaper.sh — pick a random image from Pool_Carousel/ and set it as
# the GNOME wallpaper, never repeating the image shown last time.
#
# Designed to be run from cron (once a minute). Cron has no desktop session
# environment, so we point gsettings at the user's D-Bus session bus and
# runtime dir explicitly.
#
# Usage:
#   src/rotate_wallpaper.sh            # rotate now
#   CAROUSEL_DIR=/path src/rotate_wallpaper.sh
set -euo pipefail

# --- locate the carousel folder (repo-relative by default) ---------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CAROUSEL_DIR="${CAROUSEL_DIR:-$REPO_DIR/Pool_Carousel}"
STATE_FILE="${STATE_FILE:-$REPO_DIR/.wallpaper_last}"

# --- desktop session plumbing so gsettings reaches the live session ------
UID_NUM="$(id -u)"
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$UID_NUM}"
export DBUS_SESSION_BUS_ADDRESS="${DBUS_SESSION_BUS_ADDRESS:-unix:path=$XDG_RUNTIME_DIR/bus}"

# --- gather candidate images ---------------------------------------------
shopt -s nullglob nocaseglob
mapfile -t images < <(
    for f in "$CAROUSEL_DIR"/*.png "$CAROUSEL_DIR"/*.jpg "$CAROUSEL_DIR"/*.jpeg; do
        printf '%s\n' "$f"
    done
)
shopt -u nullglob nocaseglob

if [ "${#images[@]}" -eq 0 ]; then
    echo "no images found in $CAROUSEL_DIR" >&2
    exit 1
fi

last=""
[ -f "$STATE_FILE" ] && last="$(cat "$STATE_FILE")"

# --- pick a random image that isn't the one shown last --------------------
# If there's only one image, we have no choice but to reuse it.
pick="$last"
if [ "${#images[@]}" -eq 1 ]; then
    pick="${images[0]}"
else
    while :; do
        pick="${images[RANDOM % ${#images[@]}]}"
        [ "$pick" != "$last" ] && break
    done
fi

# --- set the wallpaper (light + dark) -------------------------------------
uri="file://$(python3 -c 'import sys,urllib.parse,pathlib; print(urllib.parse.quote(str(pathlib.Path(sys.argv[1]).resolve())))' "$pick")"
gsettings set org.gnome.desktop.background picture-uri "$uri"
gsettings set org.gnome.desktop.background picture-uri-dark "$uri"

printf '%s' "$pick" > "$STATE_FILE"
echo "wallpaper -> $pick"
