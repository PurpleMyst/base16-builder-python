import os
import subprocess
import itertools
from multiprocessing.dummy import Pool

import yaml

TEMPLATES_SOURCE = "https://github.com/chriskempson/base16-templates-source"


def parse_sources(yaml_file, base_dir):
    with open(yaml_file) as f:
        data = yaml.safe_load(f)

    return [(url, os.path.join(base_dir, name)) for name, url in data.items()]


def fetch_repo(git_url, path):
    if os.path.exists(os.path.join(path, ".git")):
        subprocess.run(
            ["git", "-C", path, "pull", "-q"], env={"GIT_TERMINAL_PROMPT": "0"}
        ).check_returncode()
    else:
        subprocess.run(
            ["git", "clone", "-q", git_url, path], env={"GIT_TERMINAL_PROMPT": "0"}
        ).check_returncode()


def fetch_repos(*repos):
    Pool().starmap(fetch_repo, itertools.chain.from_iterable(repos))


def update():
    fetch_repo(TEMPLATES_SOURCE, os.path.join("sources"))

    fetch_repos(
        parse_sources(
            os.path.join("sources", "list.yaml"), os.path.join("sources", "templates")
        )
    )
