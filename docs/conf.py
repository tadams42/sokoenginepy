# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import shlex
import sys
from datetime import datetime
from pathlib import Path

_SELF_DIR = Path(__file__).parent.absolute().resolve()

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

nitpicky = True


# -- ReadTheDocs stuff -------------------------------------------------------

on_rtd = os.environ.get("READTHEDOCS", None) == "True"


# -- Project information -----------------------------------------------------

project = "sokoenginepy"
copyright = (
    ", ".join(str(y) for y in range(2017, datetime.now().year + 1))
    + ", Tomislav Adamic"
)
author = "Tomislav Adamic"
version = release = "0.6.0"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.ifconfig",
    # "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
    "m2r2",
    # "breathe",
]

needs_sphinx = "4.4"

# autodoc_type_aliases = {
#     "AnyTessellation": "sokoenginepy.AnyTessellation",
#     "TessellationOrDescription": "sokoenginepy.TessellationOrDescription",
# }
autodoc_typehints_format = "short"

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
source_suffix = {".rst": "restructuredtext", ".md": "markdown"}

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "src/libsokoengine",
    "src/sokoenginepyext",
    "src/utilities",
]

default_role = "py:obj"
add_module_names = False
pygments_style = "sphinx"
todo_include_todos = False


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
if not on_rtd:  # only import and set the theme if we're building docs locally
    import sphinx_rtd_theme

    html_theme = "sphinx_rtd_theme"
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]


# -- Extension configuration -------------------------------------------------

# -- Options for intersphinx extension ---------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# autodoc_member_order = 'bysource'
autodoc_member_order = "groupwise"

# -- Options for Doxygen C++ input -------------------------------------------

# breathe_projects = {"libsokoengine": str(_SELF_DIR / "_doxygen" / "xml")}
# breathe_default_project = "libsokoengine"
