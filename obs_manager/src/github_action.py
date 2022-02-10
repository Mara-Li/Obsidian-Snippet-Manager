"""
Provide all git actions the script needs
"""
import os.path
import sys
from pathlib import Path
import git
from git import Repo
from rich import print
from glob import glob
import yaml
import shutil
from urllib.parse import urlparse

from obs_manager.src import environment

global_value = environment.get_environments()
BASEDIR = global_value[0]
VAULT = global_value[1]


def git_clone(repo_url):
    """
    :param repo_url: The repository to clone
    :return: /
    """
    folder_name = urlparse(repo_url).path[1:].split("/")[1]
    repo = Repo.clone_from(repo_url, os.path.join(BASEDIR, str(folder_name)))
    print(f"[link={repo_url}]{repo_url}[/link] was cloned in [i u]{BASEDIR}.[/]")
    return repo.working_dir


def git_pull(repo_path):
    """
    Pull the repository to get the lasts updates.
    :param repo_path: The repo to update
    :return: /
    """
    try:
        repo = Repo(repo_path)
        snippet = repo.remotes.origin
        snippet.pull()
    except git.GitCommandError as exc:
        print(f":warning: [red] Git returns an error :[/] {exc}")
        sys.exit(1)


def move_to_obsidian(repo_path):
    """
    Move all css files in obsidian/snippet
    :param repo_path: The repo to move the files
    :return: /
    """
    snippets = os.path.join(VAULT, ".obsidian", "snippets")
    Path(snippets).mkdir(exist_ok=True)  # Create snippets folder if not exists
    # Get all css files
    css_files = [
        x
        for x in glob(os.path.join(str(repo_path), "**"), recursive=True)
        if x.endswith("css")
    ]
    if len(css_files) > 0:
        for i in css_files:
            shutil.copy(i, snippets)
    return css_files

def exclude_folder(repo_path):
    """
    Add the foldername to exclude.yml to prevent it to update.
    :param repo_path: The repo to exclude from update
    :return: /
    """
    excluded=os.path.join(BASEDIR, 'exclude.yml')
    repo_name = os.path.basename(repo_path)
    with open(excluded, 'a', encoding='utf-8') as f:
        f.write(f'- {repo_name}')
