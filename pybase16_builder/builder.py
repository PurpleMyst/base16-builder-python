import os
import functools
from glob import glob
from multiprocessing.dummy import Pool
from threading import Lock

import pystache
import yaml


def get_parent_dir(base_dir, level=1):
    for _ in range(level):
        base_dir = os.path.dirname(base_dir)

    return base_dir


def get_template_dirs():
    groups = glob(os.path.join("junk", "templates", "**", "templates", "config.yaml"))
    return {get_parent_dir(path, 2) for path in groups}


def threadsafe_cache(f):
    @functools.wraps(f)
    def inner(*args):
        with inner._lock:
            if args in inner._memo:
                return inner._memo[args]
            else:
                rv = inner._memo[args] = f(*args)
                return rv

    inner._lock = Lock()
    inner._memo = {}

    return inner


@threadsafe_cache
def get_templates(base_path):
    config_path = os.path.join(base_path, "templates", "config.yaml")

    with open(config_path) as f:
        templates = yaml.safe_load(f.read())

    for name, template in templates.items():
        mustache_path = os.path.join(get_parent_dir(config_path), f"{name}.mustache")

        with open(mustache_path) as f:
            template["parsed"] = pystache.parse(f.read())

    return templates


def get_scheme_files():
    return glob(os.path.join("junk/schemes/**/*.yaml"))


def compute_slug(scheme_file):
    scheme_basename = os.path.basename(scheme_file)
    if scheme_basename.endswith(".yaml"):
        scheme_basename = scheme_basename[: -len(".yaml")]
    return scheme_basename.lower().replace(" ", "-")


def load_scheme(scheme_file):
    with open(scheme_file) as f:
        scheme = yaml.safe_load(f)

    scheme["scheme-name"] = scheme.pop("scheme")
    scheme["scheme-author"] = scheme.pop("author")
    scheme["scheme-slug"] = compute_slug(scheme_file)

    bases = [f"base{x:02X}" for x in range(0, 16)]
    for base in bases:
        scheme[f"{base}-hex"] = scheme.pop(base)

        scheme[f"{base}-hex-r"] = scheme[f"{base}-hex"][0:2]
        scheme[f"{base}-hex-g"] = scheme[f"{base}-hex"][2:4]
        scheme[f"{base}-hex-b"] = scheme[f"{base}-hex"][4:6]

        scheme[f"{base}-rgb-r"] = str(int(scheme[f"{base}-hex-r"], 16))
        scheme[f"{base}-rgb-g"] = str(int(scheme[f"{base}-hex-g"], 16))
        scheme[f"{base}-rgb-b"] = str(int(scheme[f"{base}-hex-b"], 16))

        scheme[f"{base}-dec-r"] = str(int(scheme[f"{base}-rgb-r"]) / 255)
        scheme[f"{base}-dec-g"] = str(int(scheme[f"{base}-rgb-g"]) / 255)
        scheme[f"{base}-dec-b"] = str(int(scheme[f"{base}-rgb-b"]) / 255)

    return scheme


def build_single(scheme_file, template_group_files):
    scheme = load_scheme(scheme_file)

    scheme_name = scheme["scheme-name"]
    scheme_slug = scheme["scheme-slug"]

    print(f"Building colorschemes for scheme {scheme_name!r} ...")

    for group_path in template_group_files:
        name = os.path.basename(group_path.rstrip("/"))

        for template in get_templates(group_path).values():
            output_dir = os.path.join("output", name, template["output"])

            os.makedirs(output_dir, exist_ok=True)

            filepath = f"base16-{scheme_slug}{template.get('extension', '')}"
            filepath = os.path.join(output_dir, filepath)
            with open(filepath, "w") as f:
                f.write(pystache.render(template["parsed"], scheme))

    print(f"Built colorschemes for scheme {scheme_name!r}")


def build_concurrently(schemes, templates):
    Pool().starmap(build_single, ((scheme, templates) for scheme in schemes))


def build():
    os.makedirs("output", exist_ok=True)
    build_concurrently(get_scheme_files(), get_template_dirs())
