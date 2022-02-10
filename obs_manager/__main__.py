"""
The main function of the script.
"""

import argparse
import os
import sys
from glob import glob
from pathlib import Path
from rich.console import Console
from obs_manager.src import environment, github_action
import yaml


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
        action="store_true",
    )
    parser_update = subparser.add_parser(
        "update", help="Update a specific CSS snippet."
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
        environment.create_env()
        sys.exit()
    global_value = environment.get_environments()
    BASEDIR = global_value[0]
    exclude_file = os.path.join(BASEDIR, "exclude.yml")
    exclude = []
    if os.path.isfile(exclude_file):
        with open(exclude_file, "r", encoding="utf-8") as f:
            exclude = yaml.safe_load(f)
    else:
        f = open(exclude_file, "w", encoding="utf-8")
        f.close()
    if args.cmd == "exclude":
        exclude = args.exclude + exclude
    if args.cmd == "clone":
        repo_path = github_action.git_clone(args.repository)
        css_file = github_action.move_to_obsidian(repo_path)
        if len(css_file) > 0:
            console.print(f"🎉 [u]{args.repository}[/] successfull added to Obsidian.")
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
            github_action.git_pull(repo_path)
            css_file = github_action.move_to_obsidian(repo_path)
            if args.excluded:
                github_action.exclude_folder(repo_path)
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
                github_action.git_pull(i)
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
