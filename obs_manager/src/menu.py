"""
Create a GUI to allow an easy control for any user :D
"""
import yaml
import tkinter as tk
from PIL import Image
from PIL import ImageTk
from tkinter import ttk, filedialog
from ttkthemes import ThemedTk
import obs_manager as manager
from tkinter.messagebox import showerror, showinfo
import os.path
from glob import glob
from pathlib import Path
from obs_manager.src import github_action
from urllib.parse import urlparse

from dotenv import dotenv_values

root = ThemedTk(theme="breeze")
root.title("Obsidian Snippets Manager")
image_path = os.path.join(manager.__path__[0], "GUI", "hand.png")
root.iconphoto(True, tk.PhotoImage(file=image_path))
menu = ttk.Notebook(root)
menu.grid()

# Tab :
# 1. Update (main)
# 2. Clone - download
# 3. Delete
# 4. Configuration

update = ttk.Frame(menu)
update.grid()

clone = ttk.Frame(menu)
clone.grid()

delete = ttk.Frame(menu)
delete.grid()

config = ttk.Frame(menu)
config.grid()

menu.add(update, text="Update")
menu.add(clone, text="Clone")
menu.add(delete, text="Exclude")
menu.add(config, text="Configuration")

# CONFIGURATION MENU
def browsefunc(entry):
    entry.delete(0, "end")
    filename = filedialog.askdirectory(parent=config)
    filename = str(Path(filename))
    entry.insert("end", filename)


def save(vault, folder_snippet):
    basedir = manager.__path__[0]
    env_path = Path(f"{basedir}/.obsidian-snippet-manager")
    if (
        vault == ""
        or not os.path.isdir(Path(vault))
        or not os.path.isdir(os.path.join(vault, ".obsidian"))
    ):
        showerror(title="❌❌❌❌❌❌", message="Invalid vault path !")
    elif folder_snippet == "" or not os.path.isdir(Path(folder_snippet)):
        showerror(title="❌❌❌❌❌❌", message="Invalid Manager Snippet path !")
    elif (
        vault == ""
        or not os.path.isdir(Path(vault))
        or folder_snippet == ""
        or not os.path.isdir(Path(folder_snippet))
    ):
        showerror(title="Error", message="Invalid path for both !")
    else:
        with open(env_path, "w", encoding="utf-8") as env:
            env.write(f"vault={vault}\n")
            env.write(f"folder_snippet={folder_snippet}\n")
        excluded = os.path.join(folder_snippet, "exclude.yml")
        if not os.path.isfile(Path(excluded)):
            f = open(excluded, "w", encoding="utf-8")
            f.close()
        snippets = os.path.join(VAULT, ".obsidian", "snippets")
        Path(snippets).mkdir(exist_ok=True)  # Create snippets folder if not exists


browse_path = os.path.join(manager.__path__[0], "GUI", "folder.png")
browse_icon = Image.open(browse_path).resize((18, 18), Image.ANTIALIAS)
browse_png = ImageTk.PhotoImage(browse_icon)


def get_environment():
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
                VAULT = Path(vault_str)
                BASEDIR = Path(basedir_str)
        except RuntimeError:
            BASEDIR = Path(env["folder_snippet"])
            VAULT = Path(env["vault"])
    else:
        BASEDIR = ""
        VAULT = ""
    return BASEDIR, VAULT


config1 = ttk.Label(
    config, text="Vault Path", font=("Ubuntu", 10, "bold"), justify=tk.LEFT, anchor="w"
)
config1.grid(row=0, column=1, ipadx=5, sticky=tk.W)
vault_ui = ttk.Entry(config, font=40)
BASEDIR, VAULT = get_environment()
vault_ui.grid(row=0, column=2, ipadx=100)
vault_ui.insert("end", str(VAULT))
b1 = ttk.Button(
    config,
    text="browse",
    command=lambda: browsefunc(vault_ui),
    image=browse_png,
    padding=3,
)
b1.grid(row=0, column=3)

config2 = ttk.Label(
    config,
    text="Folder Manager",
    font=("Ubuntu", 10, "bold"),
    justify=tk.LEFT,
    anchor="w",
)
config2.grid(row=1, column=1, ipadx=5, sticky=tk.W)
manager_ui = ttk.Entry(config, font=40)
manager_ui.grid(row=1, column=2, ipadx=100)
manager_ui.insert("end", BASEDIR)

b2 = ttk.Button(
    config,
    text="browse",
    command=lambda: browsefunc(manager_ui),
    image=browse_png,
    padding=3,
)
b2.grid(row=1, column=3)

b3 = ttk.Button(
    config, text="Save", command=lambda: save(vault_ui.get(), manager_ui.get())
)
b3.grid(row=2, column=2)

# CLONE
def download(url):
    repo_path = github_action.git_clone(url)
    repo_name = urlparse(url).path[1:].split("/")[1]
    if repo_path == "0":
        showerror(title="❌❌❌❌❌❌", message=f"{repo_name} doesn't exists.")
    css_file = github_action.move_to_obsidian(repo_path)
    if len(css_file) > 0:
        showinfo(title="🎉🎉🎉🎉🎉", message=f"{repo_name} successfully added to Obsidian !")
        if clone_exclude.instate(["selected"]):
            github_action.exclude_folder(repo_path)
    else:
        showerror(title="❌❌❌❌❌❌", message=f"There is no CSS file in {repo_name}.")


clone_url = ttk.Label(
    clone, text="URL", font=("Ubuntu", 10, "bold"), justify=tk.CENTER, anchor="center"
)
clone_url.grid(row=0, column=0, ipadx=10)
clone_entry = ttk.Entry(clone, font=40)
clone_entry.grid(row=0, column=1, ipadx=150)
clone_exclude = ttk.Checkbutton(clone)
clone_exclude_label = ttk.Label(
    clone,
    text="Exclude from update",
    font=("Ubuntu", 10, "bold"),
    justify=tk.CENTER,
    anchor="e",
    padding=(50, 0, 0, 0),
)
clone_exclude_label.grid(row=1, column=1, sticky="w")
clone_exclude.grid(row=1, column=1, sticky="ne", ipadx=120)

clone_download = ttk.Button(
    clone, text="Download", command=lambda: download(clone_entry.get())
)
clone_download.grid(row=2, column=1, ipadx=120)

# UPDATE
update.grid_columnconfigure(0, weight=1)
update.grid_columnconfigure(1, weight=0)


def selection_all(tree):
    tree.selection_set(tree.get_children())


def unselect_all(tree):
    for item in tree.selection():
        tree.selection_remove(item)


def switch(tree):
    if len(tree.selection()) < len(tree.get_children()) - 1:
        tree.heading("#0", text="Unselect all Snippets")
        selection_all(tree)
    else:
        tree.heading("#0", text="Select all Snippets")
        unselect_all(tree)


def message_info(info):
    if len(info) > 1:
        info = "\n- ".join(info)
        info = "\n- " + info
    elif len(info) == 1:
        info = "".join(info)
    else:
        info = ""
    return info


def update_selected():
    data = tree.selection()
    exclude_file = os.path.join(BASEDIR, "exclude.yml")
    if os.path.isfile(exclude_file):
        with open(exclude_file, "r", encoding="utf-8") as f:
            exclude = yaml.safe_load(f)
    else:
        f = open(exclude_file, "w", encoding="utf-8")
        f.close()
    info = []
    no_css = []
    git_repo = []
    for i in data:
        if len(tree.item(i)["values"]) > 0:
            repo_path = tree.item(i)["values"][0]
            repo_name = tree.item(i)["text"]
            if (
                os.path.isdir(os.path.join(repo_path, ".git"))
                and not repo_name in exclude
            ):
                github_action.git_pull(repo_path)
                css_file = github_action.move_to_obsidian(repo_path)
                if len(css_file) > 0:
                    info.append(f"{repo_name}")
                else:
                    no_css.append(repo_name)
            else:
                git_repo.append(repo_name)
    info = message_info(info)
    no_css = message_info(no_css)
    git_repo = message_info(git_repo)
    if info != "":
        showinfo(title="Success", message=f"Successfully updated {info} !")
    if no_css != "":
        showerror(title="❌❌❌❌❌❌", message=f"There is no CSS in {no_css}")
    if git_repo != "":
        showerror(title="❌❌❌❌❌❌", message=f"There is nothing to update in: {git_repo} ")


all_repo = [x for x in glob(os.path.join(str(BASEDIR), "**")) if os.path.isdir(x)]

tree = ttk.Treeview(update)
tree.column("#0")
tree.heading(
    "#0", text="Unselect all Snippets", anchor=tk.CENTER, command=lambda: switch(tree)
)
tree.insert("", "end", "Snippets")
for i, name in enumerate(all_repo):
    tupled = (str(name),)
    repo_name = os.path.basename(name)
    tree.insert("", i, text=repo_name, values=tupled)
tree.grid(column=0, row=2, sticky="ew")
tree.selection_set(tree.get_children())
update_all = ttk.Button(
    update, text="Update selected Snippets", command=update_selected
)
update_all.grid(column=0, row=3, sticky="ew")

# EXCLUDE FILES


def exclude_selected():
    data = exclude_tree.selection()
    info = []
    for i in data:
        if len(exclude_tree.item(i)["values"]) > 0:
            repo_path = exclude_tree.item(i)["values"][0]
            repo_name = exclude_tree.item(i)["text"]
            github_action.exclude_folder(repo_path)
            info.append(repo_name)
    if len(info) == 1:
        showinfo(
            title="Success",
            message=f"{info[0]} successfully excluded from future update !",
        )
    elif len(info) > 1:
        info = "\n-" + "\n- ".join(info)
        showinfo(title="Success", message=f"Excluded from future update:{info}")


delete.grid_columnconfigure(0, weight=1)
delete.grid_columnconfigure(1, weight=0)
all_repo = [x for x in glob(os.path.join(str(BASEDIR), "**")) if os.path.isdir(x)]

exclude_tree = ttk.Treeview(delete)
exclude_tree.column("#0")
exclude_tree.heading(
    "#0",
    text="Unselect all Snippets",
    anchor=tk.CENTER,
    command=lambda: switch(exclude_tree),
)
exclude_tree.insert("", "end", "Snippets")
for i, name in enumerate(all_repo):
    tupled = (str(name),)
    repo_name = os.path.basename(name)
    exclude_tree.insert("", i, text=repo_name, values=tupled)
exclude_tree.grid(column=0, row=2, sticky="ew")
exclude_tree.selection_set(exclude_tree.get_children())
exclude_button = ttk.Button(
    delete, text="Add to excluded selected snippets", command=exclude_selected
)
exclude_button.grid(column=0, row=3, sticky="ew")

root.mainloop()
