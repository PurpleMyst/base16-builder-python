# thanks to https://gist.github.com/coleifer/33484bff21c34644dae1 for the
# original version of this code

import colorsys
import math
import itertools
import random
from collections import namedtuple

from PIL import Image
from termcolor import cprint

Point = namedtuple("Point", ("coords", "ct"))
Cluster = namedtuple("Cluster", ("points", "center"))


def rgb_to_hex(rgb):
    return "".join(format(p, "02x") for p in rgb)


def euclidean_dist(p1, p2):
    return math.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(p1.coords, p2.coords)))


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

        cprint(f"\tDifference: {diff:.2f}/{min_diff:.2f}", "yellow")

        if diff <= min_diff:
            break

    return clusters


def normalize(rgb, minv=128, maxv=256):
    h, s, v = colorsys.rgb_to_hsv(*map(lambda x: x / 256, rgb))

    v = min(max(v, minv / 256), maxv / 256)

    rgb = map(lambda x: int(x * 256), colorsys.hsv_to_rgb(h, s, v))

    return rgb_to_hex(rgb)


def generate_colorscheme(wallpaper_file):
    cprint(f"Generating colorscheme from {wallpaper_file} ...", "green")
    img = Image.open(wallpaper_file)
    img.thumbnail((256, 256))
    w, h = img.size
    points = [Point(color, count) for count, color in img.getcolors(maxcolors=w * h)]
    clusters = kmeans(points, 16, 1)
    colors = (map(int, c.center.coords) for c in clusters)

    colorscheme = {"scheme": "wallpaper", "author": "PurpleMyst"}
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
        colorscheme[f"base{i:02X}"] = color

    return colorscheme
