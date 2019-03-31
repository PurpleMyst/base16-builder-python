import os
import subprocess
import shutil
import itertools
from multiprocessing.dummy import Pool

import yaml


def yaml_to_job_list(yaml_file, base_dir):
    with open(yaml_file) as f:
        data = yaml.safe_load(f)
    return [(url, os.path.join(base_dir, name)) for name, url in data.items()]


def git_clone(git_url, path):
    if os.path.exists(os.path.join(path, ".git")):
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)

    print(f"Cloning from {git_url}…")
    subprocess.run(
        ["git", "clone", "-q", git_url, path], env={"GIT_TERMINAL_PROMPT": "0"}
    ).check_returncode()


def git_clone_job_list(*job_list):
    Pool().starmap(git_clone, itertools.chain.from_iterable(job_list))


def update():
    os.makedirs("junk", exist_ok=True)

    print("Creating sources.yaml…")
    sources = {
        "schemes": "https://github.com/chriskempson/base16-schemes-source",
        "templates": "https://github.com/chriskempson/base16-templates-source",
    }

    sources_file = os.path.join("junk", "sources.yaml")

    with open(sources_file, "w") as f:
        f.write(yaml.safe_dump(sources))

    print("Cloning sources…")
    git_clone_job_list(yaml_to_job_list(sources_file, os.path.join("junk", "sources")))

    print("Cloning templates & schemes…")
    git_clone_job_list(
        yaml_to_job_list(
            os.path.join("junk", "sources", "templates", "list.yaml"),
            os.path.join("junk", "templates"),
        ),
        yaml_to_job_list(
            os.path.join("junk", "sources", "schemes", "list.yaml"),
            os.path.join("junk", "schemes"),
        ),
    )

    print("Completed updating repositories.")
