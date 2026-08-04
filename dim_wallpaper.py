#!/usr/bin/env -S ./.venv/bin/python
# Uses the project venv. Run as ./dim_wallpaper.py ... from this folder,
# or explicitly: ./.venv/bin/python dim_wallpaper.py ...
"""Tweak an image's colors and set it as the GNOME desktop wallpaper.

Adjusts brightness/contrast/color/sharpness (Pillow's ImageEnhance API),
writes a copy with a "_dimmed" suffix, then points GNOME at it.

Examples:
    ./dim_wallpaper.py "Tide Pool.png"                 # brightness 0.5 (default dim)
    ./dim_wallpaper.py "Tide Pool.png" -b 0.7 -c 1.1   # brighter, a touch more contrast
    ./dim_wallpaper.py "Tide Pool.png" -s 0.6          # desaturate to 60%
    ./dim_wallpaper.py "Tide Pool.png" --no-wallpaper  # just write the file
"""
import argparse
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageColor, ImageEnhance


def enhance(img, brightness, contrast, color, sharpness):
    # Each factor: 1.0 = unchanged, <1 weaker, >1 stronger.
    for enhancer_cls, factor in (
        (ImageEnhance.Brightness, brightness),
        (ImageEnhance.Contrast, contrast),
        (ImageEnhance.Color, color),
        (ImageEnhance.Sharpness, sharpness),
    ):
        if factor != 1.0:
            img = enhancer_cls(img).enhance(factor)
    return img


def _split_alpha(img):
    """Return (rgb_image, alpha_or_None) so color ops leave transparency alone."""
    if img.mode == "RGBA":
        return img.convert("RGB"), img.getchannel("A")
    return img, None


def _merge_alpha(rgb, alpha):
    if alpha is None:
        return rgb
    rgb = rgb.convert("RGBA")
    rgb.putalpha(alpha)
    return rgb


def tint(img, color, strength):
    """Blend a solid `color` over the image; strength 0 = none, 1 = full color."""
    rgb, alpha = _split_alpha(img)
    overlay = Image.new("RGB", rgb.size, ImageColor.getrgb(color))
    rgb = Image.blend(rgb, overlay, strength)
    return _merge_alpha(rgb, alpha)


def hue_rotate(img, degrees):
    """Rotate all hues by `degrees` (0-360) via the HSV colour wheel."""
    rgb, alpha = _split_alpha(img)
    h, s, v = rgb.convert("HSV").split()
    shift = round(degrees / 360 * 256) % 256  # PIL's H channel is 0-255
    h = h.point(lambda p: (p + shift) % 256)
    rgb = Image.merge("HSV", (h, s, v)).convert("RGB")
    return _merge_alpha(rgb, alpha)


def set_gnome_wallpaper(path):
    uri = path.resolve().as_uri()
    for key in ("picture-uri", "picture-uri-dark"):
        subprocess.run(
            ["gsettings", "set", "org.gnome.desktop.background", key, uri],
            check=True,
        )
    return uri


def main():
    p = argparse.ArgumentParser(
        description="Dim/recolor an image and set it as the GNOME wallpaper.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("image", type=Path, help="Source image in this folder")
    p.add_argument("-b", "--brightness", type=float, default=0.5,
                   help="1.0 = unchanged, <1 darker, >1 brighter")
    p.add_argument("-c", "--contrast", type=float, default=1.0,
                   help="1.0 = unchanged, <1 flatter, >1 punchier")
    p.add_argument("-s", "--saturation", "--color", type=float, default=1.0,
                   dest="saturation",
                   help="Saturation: 1.0 = unchanged, 0 = grayscale, >1 more vivid")
    p.add_argument("-S", "--sharpness", type=float, default=1.0,
                   help="1.0 = unchanged, <1 blurrier, >1 sharper")
    p.add_argument("-t", "--tint", default=None,
                   help="Overlay colour, e.g. '#204060', 'navy', 'rgb(20,40,60)'")
    p.add_argument("-T", "--tint-strength", type=float, default=0.3,
                   help="Tint blend amount: 0 = none, 1 = full colour")
    p.add_argument("-H", "--hue", type=float, default=0.0,
                   help="Rotate all hues by this many degrees (0-360)")
    p.add_argument("-o", "--output", type=Path, default=None,
                   help="Output path (default: <name>_dimmed<ext>)")
    p.add_argument("--no-wallpaper", action="store_true",
                   help="Write the file but don't change the wallpaper")
    args = p.parse_args()

    if not args.image.is_file():
        p.error(f"no such file: {args.image}")

    out = args.output or args.image.with_name(
        f"{args.image.stem}_dimmed{args.image.suffix}"
    )

    img = Image.open(args.image)
    # ImageEnhance needs a true-color mode; palette/grayscale images blow up.
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA" if "A" in img.getbands() else "RGB")
    img = enhance(img, args.brightness, args.contrast, args.saturation, args.sharpness)
    if args.hue:
        img = hue_rotate(img, args.hue)
    if args.tint:
        img = tint(img, args.tint, args.tint_strength)
    img.save(out)
    print(f"wrote {out}")

    if not args.no_wallpaper:
        uri = set_gnome_wallpaper(out)
        print(f"wallpaper set -> {uri}")


if __name__ == "__main__":
    sys.exit(main())
