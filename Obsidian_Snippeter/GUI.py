"""
Create a GUI to allow an easy control for any user :D
"""
import os.path
import tkinter as tk
from glob import glob, iglob
from pathlib import Path
from tkinter import ttk, filedialog
from tkinter.messagebox import showerror, showinfo
from urllib.parse import urlparse

from PIL import Image
from PIL import ImageTk
from ttkthemes import ThemedTk

import Obsidian_Snippeter as manager
from Obsidian_Snippeter.src import environment as envi
from Obsidian_Snippeter.src import github_action as gt


def select_snippet(repo_path, repo_name, file_tree, tree, exclude_tree, clone_exclude, popup_list):
    not_snippet = [
        file_tree.item(i)["values"][0]
        for i in file_tree.selection()
        if len(file_tree.item(i)["values"]) > 0
    ]
    obsidian_to_css(
        repo_path, repo_name, not_snippet, tree, exclude_tree, clone_exclude, popup_list
    )


def pop_up_exclude(frame, BASEDIR, url, tree, exclude_tree, clone_exclude):
    folder_name, folder_path = download(url)
    if folder_path != "0":
        pop_list = tk.Toplevel(frame)
        pop_list.resizable(False, False)
        pop_list.title("Choose your CSS")
        pop_list.grid_columnconfigure(1, weight=2)
        pop_list.grid_columnconfigure(0, weight=1)
        file_tree = ttk.Treeview(pop_list)
        file_tree.column("#0")
        file_tree.heading(
            "#0",
            text="Unselect all snippets",
            anchor=tk.CENTER,
            command=lambda: switch(file_tree, True),
        )
        file_tree.insert("", "end", "Snippets")
        file_repo = [
            x
            for x in glob(os.path.join(BASEDIR, str(folder_name), "**"), recursive=True)
            if x.endswith(".css")
        ]
        for i, name in enumerate(file_repo):
            tupled = (str(name),)
            snippet_name = os.path.basename(name)
            file_tree.insert("", i, text=snippet_name, values=tupled)
        file_tree.grid(column=0, row=1, columnspan=2)

        if len(file_repo) > 0:
            file_tree.selection_set(file_tree.get_children())
        exclude_button = ttk.Button(
            pop_list,
            text="Clone snippets",
            command=lambda: select_snippet(
                folder_path, folder_name, file_tree, tree, exclude_tree, clone_exclude, pop_list
            ),
        )
        add_to_exclude = ttk.Button(
            pop_list,
            text="Add to excluded",
            command=lambda: exclude_selected(file_tree),
        )
        exclude_button.grid(row=2, column=0, ipadx=3)
        add_to_exclude.grid(column=1, row=2)


def git_pull(repo_path):
    """
    Pull the repository to get the lasts updates.
    :param repo_path: The repo to update
    :return: /
    """
    exc = gt.git_pull(repo_path)
    if exc != "0":
        showerror(title="WARNING", message=f"Git returns an error : {exc}")


def git_clone(repo_url):
    """
    Clone repository
    :param repo_url: Github URL to repository
    :return: Cloned directory path / info message if fail
    """
    dir, message = gt.git_clone(repo_url)
    return dir


def get_environment():
    """
    Get environment value from files
    :return: vault : Path / Basedir : Path
    """
    VAULT, BASEDIR = envi.get_environments()
    if len(str(VAULT)) == 0 or len(str(BASEDIR)) == 0 or not os.path.isdir(VAULT) or not os.path.isdir(BASEDIR):
        return "", ""
    return VAULT, BASEDIR


def browsefunc(entry, config):
    """
    Browse function to select folder path and insert in entry
    :param entry: entry to insert the path
    :param config: Configuration frame
    :return: /
    """
    entry.delete(0, "end")
    filename = filedialog.askdirectory(parent=config)
    filename = str(Path(filename))
    entry.insert("end", filename)


def save_env(vault, folder_snippet):
    """
    Save vault environment in configuration file
    create .snippets if not exists
    create exclude.yml if not exists
    :param vault: Vault path
    :param folder_snippet: Folder snippet path
    :return: /
    """
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
        showerror(title="❌❌❌❌❌❌", message="Invalid path for both !")
    else:
        with open(env_path, "w", encoding="utf-8") as env:
            env.write(f"vault={vault}\n")
            env.write(f"folder_snippet={folder_snippet}\n")
        excluded = os.path.join(folder_snippet, "exclude.yml")
        if not os.path.isfile(Path(excluded)):
            f = open(excluded, "w", encoding="utf-8")
            f.close()
        snippets = os.path.join(vault, ".obsidian", "snippets")
        Path(snippets).mkdir(exist_ok=True)  # Create snippets folder if not exists


def obsidian_to_css(
    repo_path, repo_name, not_excluded, tree, exclude_tree, clone_exclude, popup_list
):
    css_file = []

    for i in not_excluded:
        css_files = gt.move_to_obsidian(i)
        css_file.append(css_files)
    css_file = sum(css_file, [])
    css_file = [os.path.basename(x) for x in css_file]
    if len(css_file) > 0:
        css_file = "- " + "\n- ".join(css_file) + "\n"
        if len(css_file) == 1:
            css_file = "".join(css_file)
        showinfo(
            title="🎉🎉🎉🎉🎉",
            message=f"{css_file} successfully added to Obsidian !",
        )
        reload(tree)
        reload(exclude_tree)
        popup_list.quit()
        if clone_exclude.instate(["selected"]):
            gt.exclude_folder(repo_path)
    else:
        showerror(title="❌❌❌❌❌❌", message=f"There is no CSS file in {repo_name}.")


def download(url):
    """
    Clone a repository
    Move CSS to obsidian
    :param url: URL to repo
    :return: /
    """
    if len(url) != 0:
        repo_path = git_clone(url)
        repo_name = urlparse(url).path[1:].split("/")[1]

        if repo_path == "Already exists":
            showerror(title="❌❌❌❌❌❌", message=f"{repo_name} already exists.")
            return "0", "0"
        elif repo_path == "0":
            showerror(title="❌❌❌❌❌❌", message=f"{repo_name} doesn't exists.")
            return "0", "0"
        return repo_path, repo_name
    else:
        showerror(
            title="❌❌❌❌❌❌", message="Please, fill the URL before trying to download !"
        )
        return "0", "0"


def reload(tree):
    """
    Reload treeview with new contents
    Select all contents by default
    Update the select button
    :param tree: Treeview to reload
    :return: /
    """
    BASEDIR, VAULT = get_environment()
    tree.delete(*tree.get_children())
    all_repo = [x for x in glob(os.path.join(str(BASEDIR), "**")) if os.path.isdir(x)]
    if BASEDIR != "" or VAULT != "":
        traverse_dir(BASEDIR, tree)
    if len(all_repo) > 0:
        selection_all(tree)
    tree.heading("#0", text="Unselect all Snippets")


def selection_all(tree):
    """
    Select all files
    :param tree: Treeview to select files
    :return: /
    """
    tree.selection_set(tree.get_children())


def unselect_all(tree):
    """
    Unselect all files
    :param tree: Treeview to deselect contents
    :return: /
    """
    for item in tree.selection():
        tree.selection_remove(item)


def switch(tree, popup=False):
    """
    Switch between select/deselect
    :param tree: Treeview
    :param popup: If used in download popup
    :return:
    """
    tree_length = len(tree.get_children())
    if popup:
        tree_length = tree_length - 1
    if tree_length > 0:
        if len(tree.selection()) < tree_length:
            tree.heading("#0", text="Unselect all Snippets")
            selection_all(tree)
        else:
            tree.heading("#0", text="Select all Snippets")
            unselect_all(tree)


def message_info(info):
    """
    Create a message based on the length of provided info
    :param info: list of repo
    :return:
    """
    if len(info) > 1:
        info = "\n- ".join(info)
        info = "\n- " + info
    elif len(info) == 1:
        info = "".join(info)
    else:
        info = ""
    return info


def update_selected(tree):
    """
    Update the selected snippets
    :param tree: Snippet treeview
    :return: /
    """
    BASEDIR, VAULT = get_environment()
    data = tree.selection()
    exclude = gt.read_exclude(BASEDIR)
    info = []
    no_css = []
    git_repo = []
    for i in data:
        if len(tree.item(i)["values"]) > 0:
            repo_path = tree.item(i)["values"][0]
            repo_name = tree.item(i)["text"]
            if repo_path.endswith(".css"):  # isfile
                parent = str(Path(repo_path).parent)
            else:
                parent = str(repo_path)
            if os.path.isdir(os.path.join(parent, ".git")) and not repo_name in exclude:
                git_pull(parent)
                css_file = gt.move_to_obsidian(repo_path)
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
        showinfo(title="🎉🎉🎉🎉🎉", message=f"Successfully updated {info} !")
    if no_css != "":
        showerror(title="❌❌❌❌❌❌", message=f"There is no CSS in {no_css}")
    if git_repo != "":
        showerror(title="❌❌❌❌❌❌", message=f"There is nothing to update in: {git_repo} ")


def exclude_selected(exclude_tree):
    """
    Add to exclude.yml selected snippet
    :param exclude_tree: Exclude treeview
    :return:
    """
    data = exclude_tree.selection()
    info = []
    for i in data:
        if len(exclude_tree.item(i)["values"]) > 0:
            repo_path = exclude_tree.item(i)["values"][0]
            repo_name = exclude_tree.item(i)["text"]
            gt.exclude_folder(repo_path)
            info.append(repo_name)
    if len(info) == 1:
        showinfo(
            title="🎉🎉🎉🎉🎉",
            message=f"{info[0]} successfully excluded from future update !",
        )
    elif len(info) > 1:
        info = "\n-" + "\n- ".join(info)
        showinfo(title="🎉🎉🎉🎉🎉", message=f"Excluded from future update:{info}")


def configuration_menu(config, browse_png, BASEDIR, VAULT):
    """
    Create the configuration frame
    :param config: Frame
    :param browse_png: Image
    :param BASEDIR: Basedirectory
    :param VAULT: Vault directory
    :return: /
    """
    config1 = ttk.Label(
        config,
        text="Vault Path",
        font=("Ubuntu", 10, "bold"),
        justify=tk.LEFT,
        anchor="w",
    )
    config1.grid(row=0, column=1, ipadx=5, sticky=tk.W)
    vault_ui = ttk.Entry(config, font=40)
    vault_ui.grid(row=0, column=2, ipadx=100)
    vault_ui.insert("end", str(VAULT))
    b1 = ttk.Button(
        config,
        command=lambda: browsefunc(vault_ui, config),
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
        command=lambda: browsefunc(manager_ui, config),
        image=browse_png,
        padding=3,
    )
    b2.grid(row=1, column=3)

    b3 = ttk.Button(
        config, text="Save", command=lambda: save_env(vault_ui.get(), manager_ui.get())
    )
    b3.grid(row=2, column=2)


def clone_menu(clone, tree, exclude_tree, BASEDIR):
    """
    Create the clone menu
    :param clone: Frame
    :param tree: Clone treeview
    :param exclude_tree: exclude treeview
    :param BASEDIR: Base directory
    :return:
    """
    clone_url = ttk.Label(
        clone,
        text="URL",
        font=("Ubuntu", 10, "bold"),
        justify=tk.CENTER,
        anchor="center",
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
        clone,
        text="Download",
        command=lambda: pop_up_exclude(
            clone, BASEDIR, clone_entry.get(), tree, exclude_tree, clone_exclude
        ),
    )
    clone_download.grid(row=2, column=1, ipadx=120)


def check_folder_contents(folder):
    if os.path.isdir(folder):
        if not any(os.scandir(folder)):
            return False
        elif not any(iglob(os.path.join(folder, "*.css"))):
            return False
    return True


def traverse_dir(path, tree, parent=""):
    for file in os.listdir(path):
        fullpath = os.path.join(path, file)
        if not ".git" in fullpath:
            if check_folder_contents(fullpath):
                if fullpath.endswith(".css") or os.path.isdir(fullpath):
                    node_id = tree.insert(
                        parent,
                        "end",
                        text=os.path.basename(fullpath).replace(".css", ""),
                        value=(str(fullpath),),
                        open=False,
                    )
                    if os.path.isdir(fullpath):
                        traverse_dir(fullpath, tree, node_id)


def update_menu(update, BASEDIR):
    """
    Create the update menu
    :param update: Frame
    :param BASEDIR: Base directory
    :return: treeview
    """
    update.grid_columnconfigure(0, weight=1)
    update.grid_columnconfigure(1, weight=0)

    tree = ttk.Treeview(update)
    tree.column("#0")
    tree.heading(
        "#0",
        text="Unselect all Snippets",
        anchor=tk.CENTER,
        command=lambda: switch(tree),
    )
    all_repo = [x for x in glob(os.path.join(str(BASEDIR), "**")) if os.path.isdir(x)]
    if BASEDIR != "":
        traverse_dir(BASEDIR, tree)
    tree.grid(column=0, row=2, sticky="ew")
    if len(all_repo) > 0:
        tree.selection_set(tree.get_children())
    update_all = ttk.Button(
        update, text="Update selected Snippets", command=lambda: update_selected(tree)
    )
    refresh = ttk.Button(update, text="Refresh Snippets", command=lambda: reload(tree))
    update_all.grid(column=0, row=3, sticky="ew")
    refresh.grid(column=0, row=3, sticky="ne")
    return tree


def exclude_menu(delete, BASEDIR):
    """
    Create exclude menu
    :param delete: frame
    :param BASEDIR: Basedirectory
    :return: exclude treeview
    """
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
    if BASEDIR != "":
        traverse_dir(BASEDIR, exclude_tree)
    exclude_tree.grid(column=0, row=1, columnspan=2, sticky="ew")
    if len(all_repo) > 0:
        exclude_tree.selection_set(exclude_tree.get_children())
    exclude_button = ttk.Button(
        delete,
        text="Add to excluded selected snippets",
        command=lambda: exclude_selected(exclude_tree),
    )
    refresh_exclude = ttk.Button(
        delete, text="Refresh Snippets", command=lambda: reload(exclude_tree)
    )

    exclude_button.grid(column=0, row=3, sticky="ew")
    refresh_exclude.grid(column=0, row=3, sticky="ne")
    return exclude_tree


def main():
    """
    Main function to create and call GUI
    :return: /
    """
    root = ThemedTk(theme="breeze")
    root.title("Obsidian Snippets Manager")
    image_path = os.path.join(manager.__path__[0], "src", "gui_bin", "hand.png")
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
    browse_path = os.path.join(manager.__path__[0], "src", "gui_bin", "folder.png")
    browse_icon = Image.open(browse_path).resize((18, 18), Image.ANTIALIAS)
    browse_png = ImageTk.PhotoImage(browse_icon)
    BASEDIR, VAULT = get_environment()
    configuration_menu(config, browse_png, BASEDIR, VAULT)
    tree = update_menu(update, BASEDIR)
    exclude_tree = exclude_menu(delete, BASEDIR)
    clone_menu(clone, tree, exclude_tree, BASEDIR)
    root.resizable(False, False)
    root.mainloop()


if __name__ == "__main__":
    main()
