"""
The main function of the script.
"""

import argparse
import os
import sys
from glob import glob
from pathlib import Path
from rich.console import Console
from obs_manager.src import (environment, github_action)

def main():
    """
    Main function used in CLI
    :return: /
    """
    console = Console()
    parser=argparse.ArgumentParser(
        description='Git pull and copy the css files in .obsidian/snippet'
        )
    parser.add_argument('--add', '--new', '--a', help="Clone a new repository", action="store", required=False)
    parser.add_argument('--update', '--u', help='The repo you want to update', action='store', required=False)
    parser.add_argument('--config', '--c', help='Edit the configuration file', action="store_true")
    parser.add_argument('--list', help='List all Github Repository you clone.', action="store_true")
    args = parser.parse_args()
    if args.config:
        environment.create_env()
        sys.exit()
    global_value = environment.get_environments()
    BASEDIR = global_value[0]
    if args.add:
        repo_path=github_action.git_clone(args.add)
        css_file=github_action.move_to_obsidian(repo_path)
        if len(css_file) > 0:
            console.print(f'🎉 [u]{args.add}[/] successfull added to Obsidian.')
        else:
            console.print(f'🤨 There is no CSS file in {args.add}.')
    elif args.update:
        all_folder = [x for x in glob(os.path.join(str(BASEDIR), '**')) if os.path.isdir(x)]
        repo_name = [x for x in all_folder if os.path.basename(x) == args.update]
        if len(repo_name) > 0:
            repo_path = Path(repo_name[0])
            github_action.git_pull(repo_path)
            css_file=github_action.move_to_obsidian(repo_path)
            if len(css_file) > 0:
                console.print(f'🎉 [u]{args.update}[/] successfully updated.')
            else:
                console.print(f'🤨 There is no CSS file in [u]{args.update}[/].')
        else:
            console.print("[u]This repository doesn't exists[/]. Did you use the correct folder name ?")
    elif args.list:
        all_folder = [os.path.basename(x) for x in glob(os.path.join(str(BASEDIR), '**')) if
                      os.path.isdir(x)]
        if len(all_folder) > 1:
            folder_msg='\n- '.join(all_folder)
            folder_msg = f"[u] The repository present are :[/]\n- {folder_msg}"
        elif len(all_folder) == 1:
            folder_msg = ''.join(all_folder)
            folder_msg = f"The repository present is [u]{folder_msg}[/]"
        else:
            folder_msg = f"[u]There is no repository in {BASEDIR}[/]"
        console.print(folder_msg)
    else:
        all_folder = [x for x in glob(os.path.join(str(BASEDIR), '**')) if os.path.isdir(x)]
        info = []
        for i in all_folder:
            if os.path.isdir(os.path.join(i, '.git')):
                github_action.git_pull(i)
                css_file=github_action.move_to_obsidian(i)
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
