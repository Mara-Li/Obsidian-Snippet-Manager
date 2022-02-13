import sys
import os
from cx_Freeze import Executable, setup

base = None
if sys.platform == "win32":
    base = "Win32GUI"

menu = os.path.join('obs_manager', 'src', 'menu.py')
ico = os.path.join('obs_manager', 'GUI', 'hand.ico')
executables = [
    Executable(
        menu, base=base, icon=ico
    )
]

setup(
    name="Obsidian Snipper Manager",
    version="0.1",
    description="Obsidian Manager",
    executables=executables,
)
