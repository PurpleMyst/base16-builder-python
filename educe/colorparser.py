# thanks to https://gist.github.com/coleifer/33484bff21c34644dae1 for the
# original version of this code

import colorsys
import math
import itertools
import random
from collections import namedtuple

from PIL import Image

Point = namedtuple("Point", ("coords", "ct"))
Cluster = namedtuple("Cluster", ("points", "center"))

# If we're using these colors with base16, then there's a sort of "code" for each
# base. It's easy to figure this out by running `colortest`, but it's hard for
# randomly generated clusters of colors to fall into this pattern. So we
# generate colors as normal, then for each base that has an "ideal" color we
# try to find the one that's closest.
IDEAL_COLORS = {
    # base00 Black
    "base00": (0x00, 0x00, 0x00),
    # base01
    # base02
    # base03 Bright_Black
    "base03": (0xE1, 0xE1, 0xE1),
    # base04
    # base05 White
    "base05": (0xC0, 0xC0, 0xC0),
    # base06
    # base07 Bright_White
    "base07": (0xFF, 0xFF, 0xFF),
    # base08 Bright_Red
    # base08 Red
    "base08": (0xFF, 0x00, 0x00),
    # base09
    # base0A Bright_Yellow
    # base0A Yellow
    "base0A": (0xFF, 0xFF, 0x00),
    # base0B Bright_Green
    # base0B Green
    "base0B": (0x00, 0xFF, 0x00),
    # base0C Bright_Cyan
    # base0C Cyan
    "base0C": (0x00, 0xFF, 0xFF),
    # base0D Blue
    # base0D Bright_Blue
    "base0D": (0x00, 0x00, 0xFF),
    # base0E Bright_Magenta
    # base0E Magenta
    "base0E": (0xFF, 0x00, 0x00),
    # base0F
}


def rgb_to_hex(rgb):
    return "".join(format(p, "02x") for p in rgb)


def euclidean_dist(p1, p2):
    return math.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(p1.coords, p2.coords)))


def color_dist(c1, c2):
    return math.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(c1, c2)))


def _calculate_center(points):
    vals = [0, 0, 0]
    plen = 0

    for p in points:
        plen += p.ct

        for i in range(3):
            vals[i] += p.coords[i] * p.ct

    return Point([(v / plen) for v in vals], 1)


# TODO: Find a library which gives us this.
def kmeans(points, k, min_diff):
    clusters = [Cluster([p], p) for p in random.sample(points, k)]

    while True:
        plists = [[] for i in range(k)]

        for p in points:
            idx, _ = min(
                enumerate(clusters), key=lambda x: euclidean_dist(p, x[1].center)
            )

            plists[idx].append(p)

        new_clusters = [Cluster(plist, _calculate_center(plist)) for plist in plists]

        diff = max(
            euclidean_dist(old.center, new.center)
            for old, new in zip(clusters, new_clusters)
        )

        clusters = new_clusters

        if diff <= min_diff:
            break

    return clusters


def normalize(rgb, minv=128, maxv=256):
    h, s, v = colorsys.rgb_to_hsv(*map(lambda x: x / 256, rgb))

    v = min(max(v, minv / 256), maxv / 256)

    rgb = map(lambda x: int(x * 256), colorsys.hsv_to_rgb(h, s, v))

    return tuple(rgb)


def generate_colorscheme(wallpaper_file):
    img = Image.open(wallpaper_file)
    img.thumbnail((256, 256))
    w, h = img.size
    points = [Point(color, count) for count, color in img.getcolors(maxcolors=w * h)]
    clusters = kmeans(points, 16, 1)
    colors = (map(int, c.center.coords) for c in clusters)

    # XXX: Should we remove this normalization step?
    normalized_colors = []
    for i, color in enumerate(itertools.cycle(colors)):
        if i == 0:
            color = normalize(color, minv=0, maxv=32)
        elif i < 8:
            color = normalize(color, minv=160, maxv=224)
        elif i == 8:
            color = normalize(color, minv=128, maxv=192)
        elif i < 16:
            color = normalize(color, minv=200, maxv=256)
        else:
            break

        normalized_colors.append(color)

    bases = {f"base{i:02X}": None for i in range(16)}

    for base in bases:
        if base not in IDEAL_COLORS:
            continue

        idx, ideal_color = min(
            enumerate(normalized_colors),
            key=lambda x: color_dist(IDEAL_COLORS[base], x[1]),
        )

        del normalized_colors[idx]

        bases[base] = ideal_color

    # We are free to distribute the others however we wish.
    random.shuffle(normalized_colors)
    for base in bases:
        if bases[base] is None:
            bases[base] = normalized_colors.pop()

    assert not normalized_colors

    colorscheme = {base: rgb_to_hex(color) for base, color in bases.items()}
    colorscheme.update({"scheme": "wallpaper", "author": "PurpleMyst"})
    return colorscheme
