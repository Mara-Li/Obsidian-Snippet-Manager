import sys
import os
from cx_Freeze import Executable, setup

base = None
folder='Windows'
if sys.platform == "win32":
    base = "Win32GUI"
    folder = "Windows"
elif sys.platform.startswith('linux'):
    folder='Linux'
elif sys.platform.startswith('darwin'):
    folder='MacOS'
option_folder = os.path.join('app', folder)

menu = os.path.join('obs_manager', 'src', 'menu.py')
ico = os.path.join('obs_manager', 'GUI', 'hand.ico')
options = {'build_exe':{'build_exe': option_folder}}
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
    options=options
)
