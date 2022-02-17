"""
The main function of the script.
"""

import argparse
import os
import sys
from glob import glob
from pathlib import Path
from urllib.parse import urlparse

import yaml
from rich import print
from rich.console import Console

import Obsidian_Snippeter as manager
from Obsidian_Snippeter.src import environment
from Obsidian_Snippeter.src import github_action

def read_exclude(BASEDIR):
    exclude_file = os.path.join(BASEDIR, "exclude.yml")
    exclude=[]
    if os.path.isfile(exclude_file):
        with open(exclude_file, "r", encoding="utf-8") as f:
            exclude = yaml.safe_load(f)
    else:
        f = open(exclude_file, "w", encoding="utf-8")
        f.close()
    return exclude

def create_env():
    """
    Create environment variable with :
        - Vault : Absolute path to obsidian vault
        - Snippet folder : Absolute path to the folder which will contains the downloaded snippets.
    :return: /
    """
    basedir = manager.__path__[0]
    console = Console()
    env_path = Path(f"{basedir}/.obsidian-snippet-manager")
    print(f"[bold]Creating environnement in [u]{env_path}[/][/]")
    vault = ""
    folder_snippet = ""
    while (
        vault == ""
        or not os.path.isdir(vault)
        or not os.path.isdir(os.path.join(vault, ".obsidian"))
    ):
        vault = str(
            console.input(
                "Please provide your [u bold]obsidian vault[/] absolute path: "
            )
        )
    while folder_snippet == "":
        folder_snippet = str(
            console.input(
                "Please provide the [u bold]Snippet Manager Folder[/] absolute path: "
            )
        )
        if not os.path.isdir(Path(folder_snippet)):
            Path(folder_snippet).mkdir(exist_ok=True)
            console.print(
                f"[u bold]Snippet Manager Folder[/] created in [u]{folder_snippet}[/]."
            )
        excluded = os.path.join(folder_snippet, "exclude.yml")
        if not os.path.isfile(Path(excluded)):
            f = open(excluded, "w", encoding="utf-8")
            f.close()
    with open(env_path, "w", encoding="utf-8") as env:
        env.write(f"vault={vault}\n")
        env.write(f"folder_snippet={folder_snippet}\n")
    sys.exit("Environment created.")


def check_environnement():
    """
    Get environment variable from files
    :return: BASEDIR: Path / VAULT: Path
    """
    BASEDIR, VAULT = environment.get_environments()
    if len(str(BASEDIR)) == 0 or len(str(VAULT)) == 0 or not os.path.isdir(BASEDIR) or not os.path.isdir(VAULT):
        create_env()
    return BASEDIR, VAULT


def clone_message(repo_url, BASEDIR):
    """
    Rich python the info from clone return
    :param repo_url: Repository github url
    :param BASEDIR: Folder Snippet folder
    :return:
    """
    working_dir, message = github_action.git_clone(repo_url)
    repo_name = urlparse(repo_url).path[1:].split("/")[1]
    if message:
        print(f"[link={repo_url}]{repo_name}[/link] was cloned in [i u]{BASEDIR}.[/]")
    elif not message:
        if working_dir == "Already exists":
            print(f"[link={repo_url}]{repo_name}[/link] already exists !")
        else:
            print(f"[link={repo_url}]{repo_name}[/link] doesn't exists !")
    return working_dir


def pull_message(repo_path):
    """
    Print message from github action return
    :param repo_path: Path to newly cloned repo
    :return:
    """
    exc = github_action.git_pull(repo_path)
    if exc != "0":
        print(f":warning: [red] Git returns an error :[/] {exc}")


def main():
    """
    Main function used in CLI
    :return: /
    """

    class _HelpAction(argparse._HelpAction):
        def __call__(self, parser, namespace, values, option_string=None):
            parser.print_help()

            # retrieve subparsers from parser
            subparsers_actions = [
                action
                for action in parser._actions
                if isinstance(action, argparse._SubParsersAction)
            ]
            # there will probably only be one subparser_action,
            # but better save than sorry
            for subparsers_action in subparsers_actions:
                # get all subparsers and print help
                for choice, subparser in subparsers_action.choices.items():
                    print("{}".format(choice))
                    print(subparser.format_help())

            parser.exit()

    console = Console()
    parser = argparse.ArgumentParser(
        description="Git pull and copy the css files in .obsidian/snippet",
        add_help=False,
    )
    parser.add_argument(
        "--help", action=_HelpAction, help="show this help message and exit"
    )
    subparser = parser.add_subparsers(dest="cmd")
    parser_clone = subparser.add_parser(
        "clone", help="Clone a repository and add the snippet to Obsidian"
    )
    parser_clone.add_argument(
        "repository",
        help="Clone a new repository",
        action="store",
    )
    parser_clone.add_argument(
        "--excluded",
        "--e",
        "--no",
        help="Exclude this repository from update",
        action="store",
        nargs='*'
    )

    parser_update = subparser.add_parser(
        "update", help="Update a specific CSS snippet."
    )
    parser_update.add_argument(
        "--only",
        "--select",
        "--s",
        help="Use only selectionned file",
        action="store",
        nargs='+'
    )
    parser_update.add_argument(
        "repository_name",
        help="The repo you want to update",
        action="store",
    )
    parser_config = subparser.add_parser(
        "configuration", help="Edit the configuration file"
    )

    parser_list = subparser.add_parser(
        "list", help="List all Github Repository you cloned."
    )
    parser_exclude = subparser.add_parser(
        "exclude", help="Exclude repository from update"
    )
    parser_exclude.add_argument(
        "exclude", help="Exclude repository from the update", action="store", nargs="+"
    )
    args = parser.parse_args()
    if args.cmd == "config":
        create_env()
        sys.exit()
    global_value = check_environnement()
    BASEDIR = global_value[0]
    exclude = []
    if args.cmd == "exclude":
        exclude = args.exclude + read_exclude(BASEDIR)
    if args.cmd == "clone":
        repo_path = clone_message(args.repository, BASEDIR)
        if repo_path != "0" and repo_path != "Already exists":
            if args.excluded is not None:
                if len(args.excluded) > 0:
                    for i in args.excluded:
                        if i.endswith('.css'):
                            github_action.exclude_folder(i)
                        else:
                            file = i + '.css'
                            github_action.exclude_folder(file)
            css_file = github_action.move_to_obsidian(repo_path)
            if len(css_file) > 0:
                console.print(
                    f"🎉 [u]{args.repository}[/] successfull added to Obsidian."
                )
                if args.excluded is not None and len(args.excluded) > 0:
                    github_action.exclude_folder(repo_path)
            else:
                console.print(f"🤨 There is no CSS file in {args.repository}.")
    elif args.cmd == "update":
        all_folder = [
            x for x in glob(os.path.join(str(BASEDIR), "**")) if os.path.isdir(x)
        ]
        repo_name = [
            x for x in all_folder if os.path.basename(x) == args.repository_name
        ]
        if len(repo_name) > 0:
            repo_path = Path(repo_name[0])
            pull_message(repo_path)
            css_file = []
            if args.only:
                for i in args.only:
                    file = os.path.join(repo_path, i)
                    if not ".css" in i:
                        file = i + ".css"
                    css_file.append(github_action.move_to_obsidian(file))
            else:
                css_file = github_action.move_to_obsidian(repo_path)
            if len(css_file) > 0:
                console.print(f"🎉 [u]{args.repository_name}[/] successfully updated.")
            else:
                console.print(
                    f"🤨 There is no CSS file in [u]{args.repository_name}[/]."
                )
        else:
            console.print(
                "[u]This repository doesn't exists[/]. Did you use the correct folder"
                " name ?"
            )
    elif args.cmd == "list":
        all_folder = [
            os.path.basename(x)
            for x in glob(os.path.join(str(BASEDIR), "**"))
            if os.path.isdir(x)
        ]
        if len(all_folder) > 1:
            folder_msg = "\n- ".join(all_folder)
            folder_msg = f"[u] The repository present are :[/]\n- {folder_msg}"
        elif len(all_folder) == 1:
            folder_msg = "".join(all_folder)
            folder_msg = f"The repository present is [u]{folder_msg}[/]"
        else:
            folder_msg = f"[u]There is no repository in {BASEDIR}[/]"
        console.print(folder_msg)
    else:
        all_folder = [
            x for x in glob(os.path.join(str(BASEDIR), "**")) if os.path.isdir(x)
        ]
        info = []
        for i in all_folder:
            if (
                os.path.isdir(os.path.join(i, ".git"))
                and not os.path.basename(i) in exclude
            ):
                pull_message(i)
                css_file = github_action.move_to_obsidian(i)
                if len(css_file) > 0:
                    info.append(os.path.basename(i))
        if len(info) > 0:
            if len(info) > 1:
                info = "\n- ".join(info)
                console.print(f"Successfull updated :\n- [u]{info}[/]")
            else:
                info = "".join(info)
                console.print(f"Successfull updated [u]{info}[/]")
        else:
            console.print("🤨 There is no file to update in these repository")
    sys.exit()


if __name__ == "__main__":
    main()
