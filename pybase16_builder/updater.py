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
    if os.path.exists(os.path.join(path, '.git')):
        # get rid of local repo if it already exists
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)

    print(f"Cloning from {git_url}…")
    subprocess.run(["git", "clone", "-q", git_url, path],
                    env={'GIT_TERMINAL_PROMPT': '0'}).check_returncode()


def git_clone_job_list(*job_list):
    job_list = itertools.chain.from_iterable(job_list)
    Pool().starmap(git_clone, job_list)


def update():
    print("Creating sources.yaml…")
    sources = {
        "schemes": "https://github.com/chriskempson/base16-schemes-source",
        "templates": "https://github.com/chriskempson/base16-templates-source",
    }

    with open("sources.yaml", "w") as f:
        f.write(yaml.safe_dump(sources))

    print("Cloning sources…")
    git_clone_job_list(yaml_to_job_list("sources.yaml", "sources"))

    print('Cloning templates & schemes…')
    git_clone_job_list(
        yaml_to_job_list(os.path.join("sources", "templates", "list.yaml"),
                         "templates"),
        yaml_to_job_list(os.path.join("sources", "schemes", "list.yaml"),
                         "schemes")
    )

    print('Completed updating repositories.')
