from setuptools import setup, find_packages

version = "1.1.0"
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setup(
    name="Obsidian_Snippet_Manager",
    python_requires=">=3.7",
    version=version,
    description="A script to magically update your obsidian snippets hosted on github.",
    author="Mara-Li",
    author_email="mara_li@icloud.com",
    packages=find_packages(),
    install_requires=["rich", "python-dotenv", "GitPython", 'PyYAML'],
    license="AGPL",
    keywords="Obsidian, Obsidian.md, css, update, manager, obsidian snippet manager, snippets, snippet",
    classifiers=[
        "Natural Language :: English",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later"
        " (AGPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Mara-Li/Obsidian-Snippet-Manager",
    entry_points={"console_scripts": ["obsnipe=obs_manager.__main__:main"]},
)
