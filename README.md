Obsidian Snippet Manager is a python script that git pull and move CSS file in your `.obsidian/snippet` folder.

The goal is to provide a pratical way to get semi-auto-update from css snippet hosted on github, in waiting of a eventually BRAT update that support that.

# Get started
## Requirements
1. [Git](https://git-scm.com/downloads)
2. [Python](https://www.python.org/downloads/)

## Environment
The plugin needs :
- The **absolute** path of your vault, as : `G:\Drive\Vault`
- A folder that contains **all** the snippet you want to get the update.
This folder can be everywhere on your computer (yes, it can be in `.obsidian` too.). It will contain all folder of the snippet hosted on GitHub you want to use.

## How to use
1. Adding a new repo : `obs-manager --add repository_url`
2. Updating everything : `obs-manager`
3. Updating only a repository : `obs-manager --update folder_name` 
    The foldername is the folder that you want to update the snippet !

The script will :
- Git pull 
- Git move every `.css` file in your `.obsidian/snippet` folder. 

## Update on obsidian

To use directly on obsidian, you need to use [Obsidian Shell](https://github.com/Taitava/obsidian-shellcommands). 

:warning: YOU WILL LOST EVERY EDIT YOU DO ON THESES GITHUB SNIPPETS !