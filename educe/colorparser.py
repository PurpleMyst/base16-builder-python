import colorsys
import math
import random
from collections import namedtuple

import sklearn.cluster
import numpy

from PIL import Image

Point = namedtuple("Point", ("coords", "ct"))
Cluster = namedtuple("Cluster", ("points", "center"))

IDEAL_COLORS = {
    # black
    "base00": (0x00, 0x00, 0x00),
    # white
    "base07": (0xFF, 0xFF, 0xFF),
    # red
    "base08": (0xFF, 0x00, 0x00),
    # yellow
    "base0A": (0xFF, 0xFF, 0x00),
    # green
    "base0B": (0x00, 0xFF, 0x00),
    # cyan
    "base0C": (0x00, 0xFF, 0xFF),
    # blue
    "base0D": (0x00, 0x00, 0xFF),
    # magenta
    "base0E": (0xFF, 0x00, 0xFF),
}


def rgb_to_hex(rgb):
    return "".join(format(p, "02x") for p in rgb)


def lerp(x1, x2, step):
    return x1 + step * (x2 - x1)


def gradient(start, end, steps):
    h1, s1, v1 = colorsys.rgb_to_hsv(*map(lambda x: x / 256, start))
    h2, s2, v2 = colorsys.rgb_to_hsv(*map(lambda x: x / 256, end))

    for i in range(steps):
        h = lerp(h1, h2, (1 / steps) * i)
        s = lerp(s1, s2, (1 / steps) * i)
        v = lerp(v1, v2, (1 / steps) * i)

        yield tuple(map(lambda x: int(x * 256), colorsys.hsv_to_rgb(h, s, v)))


def euclidean_dist(p1, p2):
    return math.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(p1.coords, p2.coords)))


def color_dist(c1, c2):
    return math.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(c1, c2)))


def normalize(rgb, minv=128, maxv=256):
    h, s, v = colorsys.rgb_to_hsv(*map(lambda x: x / 256, rgb))

    v = min(max(v, minv / 256), maxv / 256)

    rgb = map(lambda x: int(x * 256), colorsys.hsv_to_rgb(h, s, v))

    return tuple(rgb)


def generate_colorscheme(wallpaper_file):
    img = Image.open(wallpaper_file)
    img.thumbnail((256, 256))
    w, h = img.size

    points = numpy.array(
        [[*color, count] for count, color in img.getcolors(maxcolors=w * h)]
    )
    kmeans = sklearn.cluster.KMeans(n_clusters=16, n_jobs=-1).fit(points)
    colors = [tuple(map(int, color[:3])) for color in kmeans.cluster_centers_]

    normalized_colors = []
    for i, color in enumerate(colors):
        if i == 0:
            color = normalize(color, minv=0, maxv=32)
        elif i < 8:
            color = normalize(color, minv=160, maxv=224)
        elif i == 8:
            color = normalize(color, minv=128, maxv=192)
        elif i < 16:
            color = normalize(color, minv=200, maxv=256)
        normalized_colors.append(color)

    bases = {f"base{i:02X}": None for i in range(16)}

    # Find the colors which are the closest to the colors we want.
    # For example: base08 is meant to be red, so we find the "reddest" color.
    for base, ideal_color in IDEAL_COLORS.items():
        idx, color = min(
            enumerate(normalized_colors),
            key=lambda item: color_dist(ideal_color, item[1]),
        )

        del normalized_colors[idx]

        bases[base] = color

    # Create a gradient from blackest to whitest for bases 00 to 07, to make
    # sure that contrast between them is nice and we don't end up with
    # white on slightly-whiter
    for i, base in enumerate(gradient(bases["base00"], bases["base07"], 7)):
        bases[f"base{i:02X}"] = base

    # Other colors have no special meaning, so we just take random ones.
    random.shuffle(normalized_colors)
    for base in bases:
        if bases[base] is None:
            bases[base] = normalized_colors.pop()

    colorscheme = {base: rgb_to_hex(color) for base, color in bases.items()}
    colorscheme.update({"scheme": "wallpaper", "author": "PurpleMyst"})
    return colorscheme
