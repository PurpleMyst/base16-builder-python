import colorsys
import math
import random

import sklearn.cluster
import numpy

from PIL import Image

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


def rgb_to_hsv(rgb):
    return colorsys.rgb_to_hsv(*map(lambda x: x / 255, rgb))


def hsv_to_rgb(hsv):
    return tuple(map(lambda x: int(x * 255), colorsys.hsv_to_rgb(*hsv)))


def lerp(x1, x2, step):
    return x1 + step * (x2 - x1)


def gradient(start, end, steps):
    h1, s1, v1 = rgb_to_hsv(start)
    h2, s2, v2 = rgb_to_hsv(end)

    for i in range(steps):
        step = (1 / steps) * i
        h = lerp(h1, h2, step)
        s = lerp(s1, s2, step)
        v = lerp(v1, v2, step)

        yield hsv_to_rgb((h, s, v))


def dist(c1, c2):
    return math.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(c1, c2)))


def clamp_value(rgb, minv, maxv):
    h, s, v = rgb_to_hsv(rgb)
    v = min(max(v, minv / 255), maxv / 255)
    return hsv_to_rgb((h, s, v))


def generate_palette(img_path, colors):
    img = Image.open(img_path)
    img.thumbnail((256, 256))
    w, h = img.size

    points = numpy.array(
        [[*color, count] for count, color in img.getcolors(maxcolors=w * h)]
    )
    kmeans = sklearn.cluster.KMeans(n_clusters=colors, n_jobs=-1).fit(points)

    colors = [tuple(map(int, color[:3])) for color in kmeans.cluster_centers_]
    return colors


def normalize_colors(colors):
    normalized_colors = []

    for i, color in enumerate(colors):
        if i == 0:
            color = clamp_value(color, minv=0, maxv=32)
        elif i < 8:
            color = clamp_value(color, minv=160, maxv=224)
        elif i == 8:
            color = clamp_value(color, minv=128, maxv=192)
        elif i < 16:
            color = clamp_value(color, minv=200, maxv=255)

        normalized_colors.append(color)

    return normalized_colors


def min_with_idx(l, *, key=lambda x: x):
    return min(enumerate(l), key=lambda item: key(item[1]))


def generate_colorscheme(img_path):
    colors = generate_palette(img_path, 16)
    colors = normalize_colors(colors)

    bases = {f"base{i:02X}": None for i in range(16)}

    # Find the colors which are the closest to the colors we want.
    # For example: base08 is meant to be red, so we find the "reddest" color.
    for base, ideal_color in IDEAL_COLORS.items():
        idx, color = min_with_idx(colors, key=lambda color: dist(ideal_color, color))
        del colors[idx]
        bases[base] = color

    # Create a gradient from blackest to whitest for bases 00 to 07, to make
    # sure that contrast between them is nice and we don't end up with
    # white on slightly-whiter
    for i, base in enumerate(gradient(bases["base00"], bases["base07"], 7)):
        bases[f"base{i:02X}"] = base

    # Other colors have no special meaning, so we just take random ones.
    random.shuffle(colors)
    for base in bases:
        if bases[base] is None:
            bases[base] = colors.pop()

    colorscheme = {base: rgb_to_hex(color) for base, color in bases.items()}
    colorscheme.update({"scheme": "wallpaper", "author": "PurpleMyst"})
    return colorscheme
