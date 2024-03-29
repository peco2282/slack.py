import re

from setuptools import setup

long_description: str
version: str = ""

with open("README.md", encoding="utf8") as f:
    long_description = f.read()

with open("slack/__init__.py", encoding="utf8") as f:
    search = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE)

    if search is not None:
        version = search.group(1)

    else:
        raise RuntimeError("Could not grab version string")

if not version:
    raise RuntimeError("version is not set")

requirements: list[str]
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name='wsslack.py',
    version=version,
    packages=[
        'slack',
        'slack.types',
        'slack.commands',
        'slack.view'
    ],
    install_requires=requirements,
    url='https://github.com/peco2282/slack.py',
    license='MIT',
    author='peco2282',
    author_email='pecop2282@gmail.com',
    description='An APIwrapper for slack with python.',
    long_description_content_type="text/markdown",
    long_description=long_description
)
