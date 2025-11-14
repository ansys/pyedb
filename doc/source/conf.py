# Configuration file for the PyEDB documentation builder.

import datetime
from importlib import import_module
import json
import os
import pathlib
from pprint import pformat
import shutil
import sys
import warnings

from ansys_sphinx_theme import (
    ansys_favicon,
    ansys_logo_white,
    ansys_logo_white_cropped,
    get_version_match,
    latex,
    watermark,
)
from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx import addnodes

# <-----------------Override the sphinx pdf builder---------------->
# Some pages do not render properly as per the expected Sphinx LaTeX PDF signature.
# This issue can be resolved by migrating to the autoapi format.
# Additionally, when documenting images in formats other than the supported ones,
# make sure to specify their types.
from sphinx.builders.latex import LaTeXBuilder
from sphinx.util import logging

LaTeXBuilder.supported_image_types = ["image/png", "image/pdf", "image/svg+xml", "image/webp"]

from docutils.nodes import Element
from sphinx.writers.latex import CR, LaTeXTranslator


def visit_desc_content(self, node: Element) -> None:
    self.body.append(CR + r"\pysigstopsignatures")
    self.in_desc_signature = False


LaTeXTranslator.visit_desc_content = visit_desc_content


# <----------------- End of sphinx pdf builder override---------------->

logger = logging.getLogger(__name__)


class PrettyPrintDirective(Directive):
    """Renders a constant using ``pprint.pformat`` and inserts into the document."""

    required_arguments = 1

    def run(self):
        module_path, member_name = self.arguments[0].rsplit(".", 1)

        member_data = getattr(import_module(module_path), member_name)
        code = pformat(member_data, 2, width=68)

        literal = nodes.literal_block(code, code)
        literal["language"] = "python"

        return [addnodes.desc_name(text=member_name), addnodes.desc_content("", literal)]


# Sphinx event hooks
def directory_size(directory_path):
    """Compute the size (in mega bytes) of a directory."""
    res = 0
    for path, _, files in os.walk(directory_path):
        for f in files:
            fp = os.path.join(path, f)
            res += os.stat(fp).st_size
    # Convert in mega bytes
    res /= 1e6
    return res


def remove_doctree(app, exception):
    """Remove the .doctree directory created during the documentation build."""

    # Keep the doctree to avoid creating it twice. This is typically helpful in CI/CD
    # where we want to build both HTML and PDF pages.
    if bool(int(os.getenv("SPHINXBUILD_KEEP_DOCTREEDIR", "0"))):
        logger.info(f"Keeping directory {app.doctreedir}.")
    else:
        size = directory_size(app.doctreedir)
        logger.info(f"Removing doctree {app.doctreedir} ({size} MB).")
        shutil.rmtree(app.doctreedir, ignore_errors=True)
        logger.info(f"Doctree removed.")


def adjust_image_path(app, docname, source):
    """Adjust the HTML label used to insert images in the examples.

    The following path makes the examples in the root directory work:
    # <img src="../../doc/source/_static/diff_via.png" width="500">
    However, examples fail when used through the documentation build because
    reaching the associated path should be "../../_static/diff_via.png".
    Indeed, the directory ``_static`` is automatically copied into the output directory
    ``_build/html/_static``.
    """
    # Get the full path to the document
    docpath = os.path.join(app.srcdir, docname)

    # Check if this is a PY example file
    if not os.path.exists(docpath + ".py") or not docname.startswith("examples"):
        return

    logger.info(f"Changing HTML image path in '{docname}.py' file.")
    source[0] = source[0].replace("../../doc/source/_static", "../../_static")


def check_example_error(app, pagename, templatename, context, doctree):
    """Log an error if the execution of an example as a notebook triggered an error.

    Since the documentation build might not stop if the execution of a notebook triggered
    an error, we use a flag to log that an error is spotted in the html page context.
    """
    # Check if the HTML contains an error message
    if pagename.startswith("examples") and not pagename.endswith("/index"):
        if any(
            map(
                lambda msg: msg in context["body"],
                [
                    "UsageError",
                    "NameError",
                    "DeadKernelError",
                    "NotebookError",
                    "CellExecutionError",
                ],
            )
        ):
            logger.error(f"An error was detected in file {pagename}")
            app.builder.config.html_context["build_error"] = True


def check_build_finished_without_error(app, exception):
    """Check that no error is detected along the documentation build process."""
    if app.builder.config.html_context.get("build_error", False):
        logger.info("Build failed due to an error in html-page-context")
        exit(1)


def check_pandoc_installed(app):
    """Ensure that pandoc is installed"""
    import pypandoc

    try:
        pandoc_path = pypandoc.get_pandoc_path()
        pandoc_dir = os.path.dirname(pandoc_path)
        if pandoc_dir not in os.environ["PATH"].split(os.pathsep):
            logger.info("Pandoc directory is not in $PATH.")
            os.environ["PATH"] += os.pathsep + pandoc_dir
            logger.info(f"Pandoc directory '{pandoc_dir}' has been added to $PATH")
    except OSError:
        logger.error("Pandoc was not found, please add it to your path or install pypandoc-binary")


def autodoc_skip_member(app, what, name, obj, skip, options):
    # Skip property objects that might not have __module__ attribute
    if isinstance(obj, property):
        try:
            if not hasattr(obj, "__module__"):
                return True
        except:
            return True

    try:
        exclude = True if ".. deprecated::" in obj.__doc__ else False
    except:
        exclude = False
    exclude2 = True if name.startswith("_") else False
    return True if (skip or exclude or exclude2) else None  # Can interfere with subsequent skip functions.
    # return True if exclude else None


def setup(app):
    app.add_directive("pprint", PrettyPrintDirective)
    app.connect("autodoc-skip-member", autodoc_skip_member)
    app.connect("builder-inited", check_pandoc_installed)
    app.connect("source-read", adjust_image_path)
    app.connect("html-page-context", check_example_error)
    app.connect("build-finished", remove_doctree, priority=600)
    app.connect("build-finished", check_build_finished_without_error)


local_path = os.path.dirname(os.path.realpath(__file__))
module_path = pathlib.Path(local_path)
root_path = module_path.parent.parent
try:
    from pyedb import __version__
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(local_path)))
    sys.path.append(os.path.join(root_path))
    from pyedb import __version__

project = "pyedb"
copyright = f"(c) {datetime.datetime.now().year} ANSYS, Inc. All rights reserved"
author = "Ansys Inc."
release = version = __version__
cname = os.getenv("DOCUMENTATION_CNAME", "nocname.com")
switcher_version = get_version_match(__version__)

REPOSITORY_NAME = "pyedb"
USERNAME = "ansys"
BRANCH = "main"
DOC_PATH = "doc/source"
EXAMPLES_ROOT = "examples"
EXAMPLES_PATH_FOR_DOCS = f"../../{EXAMPLES_ROOT}/"
DEFAULT_EXAMPLE_EXTENSION = "py"
GALLERY_EXAMPLES_PATH = "examples"

# Check for the local config file, otherwise use default desktop configuration
local_config_file = os.path.join(local_path, "local_config.json")
if os.path.exists(local_config_file):
    with open(local_config_file) as f:
        config = json.load(f)
else:
    config = {"run_examples": True}

# Specify environment variable to build the doc without graphical mode while
# keeping examples graphical mode activated.
os.environ["PYAEDT_NON_GRAPHICAL"] = "1"
os.environ["PYAEDT_DOC_GENERATION"] = "1"

# -- General configuration ---------------------------------------------------

# Add any Sphinx_PyEDB extension module names here as strings. They can be
# extensions coming with Sphinx_PyEDB (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.intersphinx",
    "sphinx.ext.autodoc",
    "sphinx.ext.todo",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.coverage",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx.ext.graphviz",
    "sphinx.ext.mathjax",
    "sphinx.ext.inheritance_diagram",
    "numpydoc",
    "ansys_sphinx_theme.extension.linkcode",
    "nbsphinx",
    # parse MD documents with Sphinx
    "recommonmark",
    "ansys_sphinx_theme.extension.autoapi",
]

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/reference", None),
    "numpy": ("https://numpy.org/devdocs", None),
    "matplotlib": ("https://matplotlib.org/stable", None),
    "imageio": ("https://imageio.readthedocs.io/en/stable", None),
    "pandas": ("https://pandas.pydata.org/pandas-docs/stable", None),
    "pytest": ("https://docs.pytest.org/en/stable", None),
}

toc_object_entries_show_parents = "hide"

html_show_sourcelink = True

# numpydoc configuration
numpydoc_use_plots = True
numpydoc_show_class_members = False
numpydoc_xref_param_type = True
numpydoc_validate = True
numpydoc_validation_checks = {
    # general
    "GL06",  # Found unknown section
    "GL07",  # Sections are in the wrong order.
    "GL08",  # The object does not have a docstring
    "GL09",  # Deprecation warning should precede extended summary
    "GL10",  # reST directives {directives} must be followed by two colons
    # Return
    "RT04",  # Return value description should start with a capital letter"
    "RT05",  # Return value description should finish with "."
    # Summary
    "SS01",  # No summary found
    "SS02",  # Summary does not start with a capital letter
    "SS03",  # Summary does not end with a period
    "SS04",  # Summary contains heading whitespaces
    "SS05",  # Summary must start with infinitive verb, not third person
    # Parameters
    "PR10",  # Parameter "{param_name}" requires a space before the colon
    # separating the parameter name and type",
}

# Favicon
html_favicon = ansys_favicon

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# Copy button customization ---------------------------------------------------
# exclude traditional Python prompts from the copied code
copybutton_prompt_text = r">>> ?|\.\.\. "
copybutton_prompt_is_regexp = True

# The language for content autogenerated by Sphinx_PyEDB. Refer to documentation
# for a list of supported languages.
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "sphinx_boogergreen_theme_1", "Thumbs.db", ".DS_Store", "*.txt"]

inheritance_graph_attrs = dict(rankdir="RL", size='"8.0, 10.0"', fontsize=14, ratio="compress")
inheritance_node_attrs = dict(shape="ellipse", fontsize=14, height=0.75, color="dodgerblue1", style="filled")

# -- Options for HTML output -------------------------------------------------

source_suffix = {".rst": "restructuredtext", ".md": "markdown"}

# The master toctree document.
master_doc = "index"

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# Execute notebooks before conversion
nbsphinx_execute = "auto"

# Allow errors to help debug.
nbsphinx_allow_errors = False

# Sphinx gallery customization
nbsphinx_thumbnails = {
    "examples/use_configuration/pdn_analysis": "_static/thumbnails/101_getting_started.png",
    "examples/use_configuration/serdes": "_static/thumbnails/101_getting_started.png",
    "examples/use_configuration/pcb_dc_ir": "_static/thumbnails/101_getting_started.png",
    "examples/use_configuration/dcir": "_static/thumbnails/101_getting_started.png",
    "examples/use_configuration/import_stackup": "_static/thumbnails/101_getting_started.png",
    "examples/use_configuration/import_material": "_static/thumbnails/101_getting_started.png",
    "examples/use_configuration/import_ports": "_static/thumbnails/101_getting_started.png",
    "examples/use_configuration/import_setup_ac": "_static/thumbnails/101_getting_started.png",
    "examples/use_configuration/import_padstack_definitions": "_static/thumbnails/101_getting_started.png",
    "examples/use_configuration/import_components": "_static/thumbnails/101_getting_started.png",
    "examples/use_configuration/import_sources": "_static/thumbnails/101_getting_started.png",
}

nbsphinx_custom_formats = {
    ".py": ["jupytext.reads", {"fmt": ""}],
}

exclude_patterns = [
    "conf.py",
]

# Suppress annoying matplotlib bug
warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    message="Matplotlib is currently using agg, which is a non-GUI backend, so cannot show the figure.",
)

# -- Options for HTML output -------------------------------------------------
html_short_title = html_title = "PyEDB"
html_theme = "ansys_sphinx_theme"
html_context = {
    "github_user": USERNAME,
    "github_repo": REPOSITORY_NAME,
    "github_version": BRANCH,
    "doc_path": DOC_PATH,
    "source_path": "src",
    "pyansys_tags": ["Electronics"],
}

# specify the location of your github repo
html_theme_options = {
    "logo": "pyansys",
    "switcher": {
        "json_url": f"https://{cname}/versions.json",
        "version_match": switcher_version,
    },
    "github_url": "https://github.com/ansys/pyedb",
    "navigation_with_keys": False,
    "show_prev_next": False,
    "show_breadcrumbs": True,
    "collapse_navigation": True,
    "use_edit_page_button": True,
    "additional_breadcrumbs": [
        ("PyAnsys", "https://docs.pyansys.com/"),
    ],
    "icon_links": [
        {
            "name": "Support",
            "url": "https://github.com/ansys/pyedb/discussions",
            "icon": "fa fa-comment fa-fw",
        },
        {
            "name": "Download documentation in PDF",
            "url": f"https://{cname}/version/{switcher_version}/_static/assets/download/{project}.pdf",  # noqa: E501
            "icon": "fa fa-file-pdf fa-fw",
        },
    ],
    "ansys_sphinx_theme_autoapi": {
        "project": project,
        "output": "autoapi",
        "directory": "src/pyedb",
        "add_toctree_entry": False,
        "package_depth": 1,
    },
}

html_static_path = ["_static"]

# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
html_css_files = [
    "custom.css",
]

# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "pyedbdoc"

# -- Options for LaTeX output ------------------------------------------------
# additional logos for the latex coverpage
latex_additional_files = [watermark, ansys_logo_white, ansys_logo_white_cropped]

# change the preamble of latex with customized title page
# variables are the title of pdf, watermark
latex_elements = {"preamble": latex.generate_preamble(html_title)}

linkcheck_ignore = [
    r"https://download.ansys.com/",
]

# If we are on a release, we have to ignore the "release" URLs, since it is not
# available until the release is published.
if switcher_version != "dev":
    linkcheck_ignore.append(f"https://github.com/ansys/pyedb/releases/tag/v{__version__}")  # noqa: E501
