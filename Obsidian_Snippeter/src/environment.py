import os
from pathlib import Path

from dotenv import dotenv_values

import Obsidian_Snippeter as manager


def get_environments():
    """
    Get environment variables and check them. Create the config if not exists/valid.
    :return:
        - BASEDIR : Snippet's folder absolute path.
        - VAULT : Vault absolute path.
    """
    basedir = manager.__path__[0]
    env_path = Path(f"{basedir}/.obsidian-snippet-manager")
    if os.path.isfile(env_path):
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
                    return "", ""
                VAULT = Path(vault_str)
                BASEDIR = Path(basedir_str)
        except RuntimeError:
            BASEDIR = Path(env["folder_snippet"])
            VAULT = Path(env["vault"])
        return BASEDIR, VAULT
    else:
        return "", ""
