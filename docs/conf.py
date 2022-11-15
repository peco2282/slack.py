# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

sys.path.insert(0, os.path.abspath(".."))
sys.path.append(os.path.abspath("extensions"))

project = 'slack.py'
copyright = '2022, peco2282'
author = 'peco2282'
release = '1.0.0'

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

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'basic'

rst_prolog = """
.. |coroutine| replace:: This function is a *coroutine*
"""

html_static_path = ['_static']
