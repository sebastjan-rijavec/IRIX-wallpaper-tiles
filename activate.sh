# activate.sh — set up and activate the project virtual environment.
#
# Usage (source it, don't execute it):
#     source activate.sh
#
# On first run it creates .venv and installs requirements.txt; on later
# runs it just activates the existing venv. Works in bash and zsh.

# Resolve this file's directory whether sourced from bash or zsh.
_proj="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"

if [ ! -d "$_proj/.venv" ]; then
    echo "Creating virtual environment in .venv ..."
    python3 -m venv "$_proj/.venv" || return 1 2>/dev/null || exit 1
    "$_proj/.venv/bin/pip" install --quiet --upgrade pip
    echo "Installing requirements ..."
    "$_proj/.venv/bin/pip" install --quiet -r "$_proj/requirements.txt"
    echo "Done."
fi

# shellcheck disable=SC1091
source "$_proj/.venv/bin/activate"
echo "venv active — run: python src/dim_wallpaper.py <image> [options]"
unset _proj
