import sys

from cx_Freeze import Executable, setup

base = None
if sys.platform == "win32":
    base = "Win32GUI"

executables = [
    Executable(
        "obs_manager\src\menu.py", base=base, icon="obs_manager\GUI\hand.ico"
    )
]

setup(
    name="Obsidian Snipper Manager",
    version="0.1",
    description="Obsidian Manager",
    executables=executables,
)
