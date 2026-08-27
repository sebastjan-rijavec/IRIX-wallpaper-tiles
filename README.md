# IRIX wallpaper tiles

Classic SGI IRIX pattern tiles (2560×2880), custom-made for my **LG DualUp**
monitor, plus a small Python tool to recolour any of them and set the result
as my GNOME desktop wallpaper.

## Credits

The original IRIX tile artwork comes from
[rann01/IRIX-tiles](https://github.com/rann01/IRIX-tiles); the tiles here
have been resized and recoloured for the LG DualUp aspect ratio.

## Setup

```bash
source activate.sh
```

First run creates a virtual environment in `.venv` and installs
[Pillow](https://python-pillow.org/) from `requirements.txt`; later runs
just activate it. Works in bash and zsh.

## Usage

```bash
python src/dim_wallpaper.py "tiles/Tide Pool.png"                 # brightness 0.5 (default dim)
python src/dim_wallpaper.py "tiles/Tide Pool.png" -b 0.7 -c 1.1   # brighter, more contrast
python src/dim_wallpaper.py "tiles/Tide Pool.png" -s 1.8          # more vivid
python src/dim_wallpaper.py "tiles/Tide Pool.png" -t "#204060"    # cool blue tint
python src/dim_wallpaper.py "tiles/Tide Pool.png" -H 120          # rotate hues 120°
python src/dim_wallpaper.py "tiles/Tide Pool.png" --no-wallpaper  # write file only
```

Output is written next to the source with a `_dimmed` suffix and set as
the wallpaper for both light and dark modes.

### Options

| Flag | Control | Notes |
|------|---------|-------|
| `-b` / `--brightness` | Brightness | `1.0` unchanged, `<1` darker, `>1` brighter |
| `-c` / `--contrast` | Contrast | `<1` flatter, `>1` punchier |
| `-s` / `--saturation` | Saturation | `0` grayscale, `>1` more vivid |
| `-S` / `--sharpness` | Sharpness | `<1` blurrier, `>1` sharper |
| `-t` / `--tint` | Tint colour | `#204060`, `navy`, `rgb(20,40,60)` |
| `-T` / `--tint-strength` | Tint amount | `0` none … `1` full colour |
| `-H` / `--hue` | Hue rotation | degrees `0–360` |
| `-o` / `--output` | Output path | default `<name>_dimmed<ext>` |
| `--no-wallpaper` | | write file only, don't change the desktop |

All colour factors use Pillow's `ImageEnhance` API where `1.0` means
unchanged. Transparency is preserved through tint and hue operations.
