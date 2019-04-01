import os
from glob import glob

import pystache
import yaml
from termcolor import cprint


def _get_parent_dir(base_dir, level=1):
    for _ in range(level):
        base_dir = os.path.dirname(base_dir)

    return base_dir


def _get_template_dirs():
    groups = glob(
        os.path.join("sources", "templates", "**", "templates", "config.yaml")
    )
    return {_get_parent_dir(path, 2) for path in groups}


def _get_templates(base_path):
    config_path = os.path.join(base_path, "templates", "config.yaml")

    with open(config_path) as f:
        templates = yaml.safe_load(f.read())

    for name, template in templates.items():
        mustache_path = os.path.join(_get_parent_dir(config_path), f"{name}.mustache")

        with open(mustache_path) as f:
            template["parsed"] = pystache.parse(f.read())

    return templates


def _compute_slug(scheme_file):
    scheme_basename = os.path.basename(scheme_file)
    if scheme_basename.endswith(".yaml"):
        scheme_basename = scheme_basename[: -len(".yaml")]
    return scheme_basename.lower().replace(" ", "-")


def augment_scheme(scheme):
    scheme["scheme-name"] = scheme.pop("scheme")
    scheme["scheme-author"] = scheme.pop("author")
    scheme["scheme-slug"] = _compute_slug(scheme["scheme-name"])

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


def build(scheme):
    augment_scheme(scheme)

    os.makedirs("output", exist_ok=True)

    scheme_name = scheme["scheme-name"]
    scheme_slug = scheme["scheme-slug"]

    cprint(f"Building colorschemes for scheme {scheme_name!r} ...", "green")

    for group_path in _get_template_dirs():
        name = os.path.basename(group_path.rstrip("/"))

        for template in _get_templates(group_path).values():
            output_dir = os.path.join("output", name, template["output"])

            os.makedirs(output_dir, exist_ok=True)

            filepath = f"base16-{scheme_slug}{template.get('extension', '')}"
            filepath = os.path.join(output_dir, filepath)
            with open(filepath, "w") as f:
                f.write(pystache.render(template["parsed"], scheme))

    cprint(f"Built colorschemes for scheme {scheme_name!r}", "green")
