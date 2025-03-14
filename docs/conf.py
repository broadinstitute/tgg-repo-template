import sys
from pathlib import Path

import requests
import sphinx_autodoc_typehints
from sphinx.ext import autosummary

from directives import AutoModuleSummary

sys.path.insert(0, str(Path(__file__).parent.parent))


project = "tgg-repo-template"
version = release = "main"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
    "myst_parser",
    "sphinxarg.ext",
]

# README.md contains developer documentation for building docs
exclude_patterns = ["README.md"]

master_doc = "index"

html_theme = "sphinx_rtd_theme"

html_theme_options = {
    "display_version": False,
}

html_static_path = ["_static"]

html_css_files = ["theme_overrides.css"]

html_show_sphinx = False

html_show_copyright = False

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "member-order": "bysource",
}

# Configuration for sphinx_autodoc_typehints
# Document parameter types even if the parameter is otherwise undocumented.
always_document_param_types = True

# For undocumented functions, autosummary ends up using the :param or :rtype:
# line added by sphinx_autodoc_typehints as the function's summary. This results
# in the second column of the summary table containing a <dl> element, which
# breaks the formatting.
#
# To work around this, override autosummary's extract_summary function and
# replace replace these lines with an empty string for the summary.
original_extract_summary = autosummary.extract_summary


def extract_summary(doc, document):
    summary = original_extract_summary(doc, document)
    if any(summary.startswith(tag) for tag in (":param ", ":rtype: ")):
        return ""
    return summary


autosummary.extract_summary = extract_summary


# Configuration for sphinx.ext.intersphinx
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html
intersphinx_mapping = {}

if requests.head("https://hail.is/docs/0.2/objects.inv").status_code == 200:
    intersphinx_mapping["hail"] = ("https://hail.is/docs/0.2", None)
else:
    print("Unable to link to Hail docs (cannot access objects.inv)", file=sys.stderr)

# sphinx_autodoc_typehints generates references with qualified names.
# Since Hail re-exports many objects from higher level packages/modules,
# Hail's documentation does not list all objects by their qualified name.
# For example, Table is documented as hail.Table, not hail.table.Table.
# Thus, intersphinx cannot link some of the Hail references generated by
# sphinx_autodoc_typehints.
#
# To work around this, override sphinx_autodoc_typehints's get_annotation_module
# function and map the qualified names to what Hail's documentation uses.
original_get_annotation_module = sphinx_autodoc_typehints.get_annotation_module


hail_module_map = {
    "hail.expr.expressions.base_expression": "hail.expr",
    "hail.expr.expressions.typed_expressions": "hail.expr",
    "hail.genetics.pedigree": "hail.genetics",
    "hail.genetics.reference_genome": "hail.genetics",
    "hail.linalg.blockmatrix": "hail.linalg",
    "hail.matrixtable": "hail",
    "hail.table": "hail",
    "hail.utils.struct": "hail.utils",
    "hail.utils.interval": "hail.utils",
}


def get_annotation_module(annotation):
    module = original_get_annotation_module(annotation)

    if module.startswith("hail."):
        if module in hail_module_map:
            return hail_module_map[module]

    return module


sphinx_autodoc_typehints.get_annotation_module = get_annotation_module


def setup(app):
    app.add_directive("automodulesummary", AutoModuleSummary)
