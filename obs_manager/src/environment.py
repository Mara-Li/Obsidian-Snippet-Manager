"""
Function to create environment variables.
"""
import os.path
import sys
from pathlib import Path
from rich.console import Console
from rich import print
from dotenv import dotenv_values

import obs_manager as manager


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
    while vault == "" or not os.path.isdir(vault):
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
        excluded=os.path.join(folder_snippet, 'exclude.yml')
        if not os.path.isfile(Path(excluded)):
            f=open(excluded, 'w', encoding='utf-8')
            f.close()
    with open(env_path, "w", encoding="utf-8") as env:
        env.write(f"vault={vault}\n")
        env.write(f"folder_snippet={folder_snippet}\n")
    sys.exit("Environment created.")


def get_environments():
    """
    Get environment variables and check them. Create the config if not exists/valid.
    :return:
        - BASEDIR : Snippet's folder absolute path.
        - VAULT : Vault absolute path.
    """
    basedir = manager.__path__[0]
    env_path = Path(f"{basedir}/.obsidian-snippet-manager")
    if not os.path.isfile(env_path):
        create_env()
    else:
        with open(env_path, "r", encoding="utf-8") as f:
            environments = f.read().splitlines()
            if len(environments) == 0:
                create_env()
            else:
                for data in environments:
                    vault = data.split("=")
                    if len(data) == 0 or len(vault[1]) == 0:
                        create_env()

    env = dotenv_values(env_path)
    try:
        BASEDIR = Path(env["folder_snippet"]).expanduser()
        VAULT = Path(env["vault"]).expanduser()
    except KeyError:
        with open(env_path, "r", encoding="utf-8") as f:
            vault_str = "".join(f.readlines(1)).replace("vault=", "").rstrip()
            basedir_str = (
                "".join(f.readlines(2)).replace("folder_snippet=", "").rstrip()
            )
            if (
                len(vault_str) == 0
                or len(basedir_str) == 0
                or not os.path.isdir(vault_str)
                or not os.path.isdir(basedir_str)
            ):
                sys.exit("Please provide a valid path for all config items.")
            VAULT = Path(vault_str)
            BASEDIR = Path(basedir_str)
    except RuntimeError:
        BASEDIR = Path(env["folder_snippet"])
        VAULT = Path(env["vault"])
    return BASEDIR, VAULT
