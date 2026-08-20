import simpatia

project = "simpatia"
author = "Alex Little"
release = simpatia.__version__
version = release

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "myst_parser",
    "sphinxcontrib.autodoc_pydantic",
]

html_theme = "furo"
exclude_patterns = ["_build"]

autodoc_pydantic_model_show_json = False
autodoc_pydantic_model_show_config_summary = False
autodoc_pydantic_field_list_validators = False

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pydantic": ("https://docs.pydantic.dev/latest", None),
}

myst_enable_extensions = ["colon_fence", "deflist"]