# Configuration file for the Sphinx_PyEDB documentation builder.

# -- Project information -----------------------------------------------------
import datetime
from importlib import import_module
import json
import os
import pathlib
from pprint import pformat
import sys
import warnings

from ansys_sphinx_theme import (
    ansys_favicon,
    ansys_logo_white,
    ansys_logo_white_cropped,
    get_version_match,
    latex,
    pyansys_logo_black,
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
from sphinx_gallery.sorting import FileNameSortKey

LaTeXBuilder.supported_image_types = ["image/png", "image/pdf", "image/svg+xml", "image/webp"]

from docutils.nodes import Element
from sphinx.writers.latex import CR, LaTeXTranslator


def visit_desc_content(self, node: Element) -> None:
    self.body.append(CR + r"\pysigstopsignatures")
    self.in_desc_signature = False


LaTeXTranslator.visit_desc_content = visit_desc_content


# <----------------- End of sphinx pdf builder override---------------->


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


def autodoc_skip_member(app, what, name, obj, skip, options):
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


# Specify environment variable to build the doc without grpahical mode while
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
    # TODO: Remove once we switch for new example format.
    "recommonmark",
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

# # disable generating the sphinx nested documentation
# if "PYEDB_CI_NO_AUTODOC" in os.environ:
#     templates_path.clear()

# Copy button customization ---------------------------------------------------
# exclude traditional Python prompts from the copied code
copybutton_prompt_text = r">>> ?|\.\.\. "
copybutton_prompt_is_regexp = True

# The language for content autogenerated by Sphinx_PyEDB. Refer to documentation
# for a list of supported languages.
#
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

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']

source_suffix = {".rst": "restructuredtext", ".md": "markdown"}

# The master toctree document.
master_doc = "index"

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"


# gallery build requires EDB install
if os.name != "posix" and "PYEDB_CI_NO_EXAMPLES" not in os.environ:
    # suppress annoying matplotlib bug
    warnings.filterwarnings(
        "ignore",
        category=UserWarning,
        message="Matplotlib is currently using agg, which is a non-GUI backend, so cannot show the figure.",
    )

    if config["run_examples"]:
        extensions.append("sphinx_gallery.gen_gallery")

        sphinx_gallery_conf = {
            # convert rst to md for ipynb
            "pypandoc": True,
            # path to your examples scripts
            "examples_dirs": [EXAMPLES_PATH_FOR_DOCS],
            # path where to save gallery generated examples
            "gallery_dirs": [GALLERY_EXAMPLES_PATH],
            # Pattern to search for examples files
            "filename_pattern": r"\." + DEFAULT_EXAMPLE_EXTENSION,
            # Remove the "Download all examples" button from the top level gallery
            "download_all_examples": False,
            # Sort gallery examples by file name instead of number of lines (default)
            "within_subsection_order": FileNameSortKey,
            # directory where function granular galleries are stored
            "backreferences_dir": None,
            # Modules for which function level galleries are created.  In
            "doc_module": "ansys-legacy",
            "image_scrapers": ("matplotlib"),
            "ignore_pattern": "flycheck*",
            "thumbnail_size": (350, 350),
        }

# jinja_contexts = {
#     "main_toctree": {
#         "run_examples": config["run_examples"],
#     },
# }
# def prepare_jinja_env(jinja_env) -> None:
#     """
#     Customize the jinja env.
#
#     Notes
#     -----
#     See https://jinja.palletsprojects.com/en/3.0.x/api/#jinja2.Environment
#     """
#     jinja_env.globals["project_name"] = project
#
#
# autoapi_prepare_jinja_env = prepare_jinja_env

# -- Options for HTML output -------------------------------------------------
html_short_title = html_title = "PyEDB"
html_theme = "ansys_sphinx_theme"
html_logo = pyansys_logo_black
html_context = {
    "github_user": USERNAME,
    "github_repo": REPOSITORY_NAME,
    "github_version": BRANCH,
    "doc_path": DOC_PATH,
    "source_path": "src",
}

# specify the location of your github repo
html_theme_options = {
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
    "use_meilisearch": {
        "api_key": os.getenv("MEILISEARCH_PUBLIC_API_KEY", ""),
        "index_uids": {
            f"pyedb-v{get_version_match(__version__).replace('.', '-')}": "PyEDB",
        },
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
