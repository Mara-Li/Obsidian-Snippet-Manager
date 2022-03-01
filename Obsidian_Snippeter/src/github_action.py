"""
Provide all git actions the script needs
"""
import yaml
import validators
import os.path
import shutil
from glob import glob
from pathlib import Path
from urllib.parse import urlparse

import git
from git import Repo, exc
from Obsidian_Snippeter.src import environment


def read_exclude(BASEDIR):
    exclude_file = os.path.join(BASEDIR, "exclude.yml")
    if os.path.isfile(exclude_file):
        with open(exclude_file, "r", encoding="utf-8") as f:
            exclude = yaml.safe_load(f)
        if exclude is None:
            exclude = []
    else:
        f = open(exclude_file, "w", encoding="utf-8")
        f.close()
        exclude = []
    return exclude


def git_clone(repo_url):
    """
    :param repo_url: The repository to clone
    :return: /
    """
    global_value = environment.get_environments()
    BASEDIR = global_value[0]
    if len(repo_url) > 0 and validators.url(repo_url):
        folder_name = urlparse(repo_url).path[1:].split("/")[1]
        if os.path.isdir(os.path.join(BASEDIR, str(folder_name))):
            return "Already exists", False
        try:
            repo = Repo.clone_from(repo_url, os.path.join(BASEDIR, str(folder_name)))
            return repo.working_dir, True
        except exc.GitCommandError:
            return "0", False
    else:
        return "0", False


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
        return "0"
    except git.GitCommandError as exc:
        return exc


def move_to_obsidian(repo_path):
    """
    Move all css files in obsidian/snippet
    :param repo_path: The repo to move the files
    :return: /
    """
    global_value = environment.get_environments()
    VAULT = global_value[1]
    BASEDIR = global_value[0]
    snippets = os.path.join(VAULT, ".obsidian", "snippets")
    exclude = read_exclude(BASEDIR)
    Path(snippets).mkdir(exist_ok=True)  # Create snippets folder if not exists
    # Get all css files
    css_files = []
    if not os.path.isfile(repo_path):
        css_files = [
            x
            for x in glob(os.path.join(str(repo_path), "**"), recursive=True)
            if x not in exclude and x.endswith(".css")
        ]
    elif os.path.isfile(repo_path) and not str(repo_path) in exclude:
        css_files = [repo_path]
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
    global_value = environment.get_environments()
    BASEDIR = global_value[0]
    excluded = os.path.join(BASEDIR, "exclude.yml")
    repo_name = os.path.basename(repo_path)
    excluded_files = read_exclude(BASEDIR)
    if repo_name not in excluded_files and repo_name != "":
        excluded_files.append(repo_name)
    with open(excluded, "w", encoding="utf-8") as f:
        yaml.dump(excluded_files, f)
