"""Author the two Maps SVG masters from the pinned NASA textures and deck outlines."""

import argparse
from base64 import b64encode
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
WIDTH, HEIGHT = 2010, 1340
TEXTURES = {
    "blue.jpg": "926be7253be90a1fd57071a33afbfe7a712a2dfe0d5b5b4602bc5dfbcfdc2c89",
    "black.jpg": "230aac448ae68c358be433dd518888cccb3a85ccf66f7b44326441c324ad6725",
}
X, Y = np.meshgrid(np.arange(WIDTH, dtype=np.float32) + .5,
                   np.arange(HEIGHT, dtype=np.float32) + .5)


def texture(path):
    data = path.read_bytes()
    if sha256(data).hexdigest() != TEXTURES[path.name]:
        raise ValueError(f"Unexpected NASA source checksum: {path.name}")
    # These two identified inputs are large global rasters. Decode the day texture at half size.
    limit = Image.MAX_IMAGE_PIXELS
    try:
        Image.MAX_IMAGE_PIXELS = None
        with Image.open(BytesIO(data)) as image:
            image.draft("RGB", (10000, 5000))
            return np.asarray(image.convert("RGB"))
    finally:
        Image.MAX_IMAGE_PIXELS = limit


def sample(rgb, lon, lat):
    """Bilinearly sample a global equirectangular raster at radians lon/lat."""
    h, w = rgb.shape[:2]
    u = (lon / (2 * np.pi) + .5) * w - .5
    v = np.clip((.5 - lat / np.pi) * h - .5, 0, h - 1)
    ui = np.floor(u).astype(np.int32)
    vi = np.floor(v).astype(np.int32)
    du = (u - ui).astype(np.float32)[..., None]
    dv = (v - vi).astype(np.float32)[..., None]
    below = np.minimum(vi + 1, h - 1)
    left, right = ui % w, (ui + 1) % w
    return ((rgb[vi, left] * (1-du) + rgb[vi, right] * du) * (1-dv)
            + (rgb[below, left] * (1-du) + rgb[below, right] * du) * dv)


def smooth(value):
    t = np.clip(value, 0, 1)
    return t*t*(3-2*t)


def mix(a, b, amount):
    return a * (1 - amount[..., None]) + b * amount[..., None]


def canada(day, night):
    cx, cy, radius = 918, 1130, 1035
    lat0, lon0 = np.deg2rad([25, -104])
    u, v = (X-cx)/radius, (cy-Y)/radius
    r = np.hypot(u, v)
    z = np.sqrt(np.maximum(0, 1-r*r))
    lat = np.arcsin(np.clip(v*np.cos(lat0) + z*np.sin(lat0), -1, 1))
    lon = lon0 + np.arctan2(u, z*np.cos(lat0) - v*np.sin(lat0))
    sun = -.65*u + .14*v + .66*z
    blue = sample(day, lon, lat)
    # Lift only the dark blue water in the day raster; keep the land and snow colours.
    water = smooth((blue[..., 2] - blue[..., 0] - 3)/11) * (1-smooth((blue[..., 1]-38)/32))
    blue = blue + water[..., None] * np.array([15, 32, 45], dtype=np.float32)
    black = sample(night, lon, lat) * np.array([.64, .70, .91], dtype=np.float32)
    world = mix(black, blue, smooth((sun-.01)/.31))
    world *= (.78 + .22*smooth((sun+.10)/.60))[..., None]
    # The sunlit edge catches a thin atmospheric rim over an otherwise empty sky.
    rim = smooth((r-.86)/.14) * smooth((sun+.15)/.62) * .53
    world = mix(world, np.array([138, 173, 206], dtype=np.float32), rim)
    sky = np.array([8, 11, 19], dtype=np.float32)
    air = np.exp(-np.maximum(0, r-1)*280) * smooth((sun+.04)/.55)
    space = mix(sky, np.array([82, 115, 153], dtype=np.float32),
                np.where(r < 1.012, air*.43, 0))
    rgb = mix(space, world, smooth((1-r)*radius+.5))

    def project(lon, lat):
        delta = lon - lon0
        return (cx + radius*np.cos(lat)*np.sin(delta),
                cy - radius*(np.cos(lat0)*np.sin(lat)-np.sin(lat0)*np.cos(lat)*np.cos(delta)))

    return rgb, project


def thailand(day, night):
    lon0, lat0 = np.deg2rad([100.1, 13.2])
    scale = 2930  # pixels per radian in this north-up Mercator view
    cx, cy = 933, 622

    def mercator(lat):
        return np.arcsinh(np.tan(lat))

    lon = lon0 + (X-cx)/scale
    lat = np.arctan(np.sinh(mercator(lat0) + (cy-Y)/scale))
    blue = sample(day, lon, lat)
    black = sample(night, lon, lat)
    lights = np.maximum(black - np.array([12, 17, 27], dtype=np.float32), 0)
    terrain = blue @ np.array([.27, .57, .16], dtype=np.float32)
    base = np.array([9, 11, 17], dtype=np.float32) + terrain[..., None] * np.array([.087, .102, .143], dtype=np.float32)
    rgb = base + lights * np.array([.92, .88, .75], dtype=np.float32)
    # Tone the distant north-east context into the sea-dark margin for the pill.
    quiet = smooth((X-1175)/415) * (1-smooth((Y-350)/440))
    rgb = mix(rgb, np.array([15, 18, 25], dtype=np.float32), quiet)

    def project(lon, lat):
        return cx+(lon-lon0)*scale, cy-(mercator(lat)-mercator(lat0))*scale

    return rgb, project


def outline(polygons, project):
    parts = []
    bounds = []
    for polygon in polygons:
        for ring in polygon:
            lon, lat = np.deg2rad(np.array(ring).T)
            x, y = project(lon, lat)
            if max(np.ptp(x), np.ptp(y)) < 1.6:
                continue
            bounds.append((min(x), min(y), max(x), max(y)))
            parts.append("M" + " ".join(f"{a:.1f},{b:.1f}" for a, b in zip(x, y)) + "Z")
    if any(x0 < 221 or y0 < 228 or x1 > 1789 or y1 > 1112 for x0, y0, x1, y1 in bounds):
        raise ValueError(f"Outline outside safe area: {np.array(bounds).min(axis=0)}, {np.array(bounds).max(axis=0)}")
    return "".join(parts)


def write_master(path, rgb, stroke, width):
    with BytesIO() as buffer:
        Image.fromarray(np.clip(rgb + .5, 0, 255).astype(np.uint8)).save(
            buffer, format="JPEG", quality=96, subsampling=0, optimize=True)
        backdrop = b64encode(buffer.getvalue()).decode("ascii")
    path.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">\n'
        f'<defs><path id="outline" d="{stroke}"/></defs>\n'
        f'<image width="{WIDTH}" height="{HEIGHT}" xlink:href="data:image/jpeg;base64,{backdrop}"/>\n'
        '<g stroke-linecap="round" stroke-linejoin="round">\n'
        f'<use xlink:href="#outline" fill="#ffda79" fill-opacity=".035" fill-rule="evenodd" '
        f'stroke="#28231c" stroke-opacity=".87" stroke-width="{width + 3}"/>\n'
        f'<use xlink:href="#outline" fill="none" stroke="#ffdb84" stroke-width="{width}"/>\n'
        '</g>\n</svg>\n', encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--textures", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    day, night = (texture(args.textures / name) for name in TEXTURES)
    places = {p["code"]: p for p in json.loads((ROOT / "source/places.json").read_text())}
    args.output.mkdir(parents=True, exist_ok=False)
    for i, (code, render, line_width) in enumerate((("CAN", canada, 4.2), ("THA", thailand, 5.4)), 1):
        rgb, project = render(day, night)
        geometry = json.loads(places[code]["field"])["outline"]
        assert geometry["type"] == "MultiPolygon"
        write_master(args.output / f"rv-map-cover-{i}.svg",
                     rgb, outline(geometry["coordinates"], project), line_width)


if __name__ == "__main__":
    main()
