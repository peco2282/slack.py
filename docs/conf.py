# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import re
import sys

sys.path.insert(0, os.path.abspath(".."))
sys.path.append(os.path.abspath("extensions"))

project = 'slack.py'
copyright = '2022, peco2282'
author = 'peco2282'

with open("../slack/__init__.py", encoding="utf8") as f:
    search = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE)

    if search is not None:
        _version = search.group(1)

    else:
        raise RuntimeError("Could not grab version string")
release = _version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "builder",
    "sphinx.ext.autodoc",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinxcontrib_trio",
    "details",
    "exception_hierarchy",
    "attributetable",
    "resourcelinks",
    "nitpick_file_ignorer",
    "myst_parser",
]
master_doc = "index"
pygments_style = "friendly"

source_suffix = {
    ".rst": "restructuredtext",  # Used For The Other Docs
    ".md": "markdown",  # Used ONLY In the Guide For Faster Making Time
}

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

napoleon_numpy_docstring = True
html_favicon = "./img/icon.ico"
html_logo = "./img/icon.ico"
# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'basic'

intersphinx_mapping = {
    "py": ("https://docs.python.org/3", None),
}


rst_prolog = """
.. |coroutine| replace:: This function is a *coroutine*
.. |coro| replace:: This function is a *coroutine*

"""

html_static_path = ['_static']

resource_links = {
    "slack": "https://api.slack.com",
    "element": "https://api.slack.com/reference/block-kit/block-elements",
    "handling": "https://api.slack.com/interactivity/handling",
    "object": "https://api.slack.com/reference/block-kit/composition-objects",
    "action": "https://api.slack.com/reference/interaction-payloads/block-actions"
}
