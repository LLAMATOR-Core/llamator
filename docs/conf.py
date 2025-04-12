# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
project = 'LLAMATOR'
copyright = '2025, Neronov Roman, Nizamov Timur, Ivanov Nikita'
author = 'Neronov Roman, Nizamov Timur, Ivanov Nikita'

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.napoleon",         # support for google style docstrings
    "sphinx.ext.autodoc",          # auto* are for automatic code docs generation
    "sphinx.ext.autosummary",      # as above
    "sphinx.ext.intersphinx",      # allows to cross reference other sphinx documentations
    "sphinx.ext.autosectionlabel", # each doc section gets automatic reference generated
    "myst_parser",                 # adds support for Markdown
    "sphinx.ext.extlinks",
    "sphinx.ext.mathjax",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for TODOs -------------------------------------------------------
todo_include_todos = False

# -- Options for Markdown files ----------------------------------------------
myst_enable_extensions = [
    "colon_fence",
    "deflist",
]
myst_heading_anchors = 3

# -- Options for HTML output -------------------------------------------------
html_theme = "furo"
html_static_path = ["_static"]

html_logo = "../assets/LLAMATOR.svg"

html_title = "LLAMATOR"

html_theme_options = {
    "light_css_variables": {
        "color-background-primary": "#f8f5fa",  # Very light pinkish purple background
        "color-background-secondary": "#f0ebf3",  # Slightly darker pinkish purple
        "color-foreground-primary": "#2d1b36",  # Very dark purple for primary text
        "color-foreground-secondary": "#432952",  # Dark purple for secondary text
        "color-brand-primary": "#2d1b36",  # Very dark purple
        "color-brand-content": "#432952",  # Dark purple
        "color-link": "#614378",  # Purple for links
        "color-link-hover": "#7b5696",  # Lighter purple on hover
        "color-admonition-background": "#fff9fc",  # Very light pink background for notes
        "color-admonition-title-background": "#2d1b36",  # Very dark purple for the title
        "color-admonition-title": "#ffffff",  # White text on dark background
        "color-admonition-border": "#2d1b36",  # Very dark purple for the border
        "color-code-background": "#f5f0f7",  # Light pinkish purple background for code
        "color-code-foreground": "#2d1b36",  # Very dark purple code text
        "color-sidebar-background": "#f5f0f7",  # Light pinkish purple sidebar background
        "color-sidebar-item-background--hover": "#ebe4ef",  # On menu item hover
        "color-sidebar-item-expander-background--hover": "#e0d7e6",  # On hover over a drop-down element
        "color-sidebar-search-background": "#fff9fc",  # Very light pink search background
        "color-sidebar-search-background--focus": "#fff9fc",  # Same on focus
    },
    "dark_css_variables": {
        "color-background-primary": "#1a1b24",
        "color-background-secondary": "#44475a",
        "color-foreground-primary": "#f8f8f2",
        "color-foreground-secondary": "#6272a4",
        "color-brand-primary": "#bd93f9",
        "color-brand-content": "#ff79c6",
        "color-link": "#8be9fd",
        "color-link-hover": "#ff79c6",
        "color-admonition-background": "#282a36",
        "color-admonition-title-background": "#44475a",
        "color-admonition-title": "#f8f8f2",
        "color-admonition-border": "#6272a4",
        "color-code-background": "#282a36",
        "color-code-foreground": "#f8f8f2",
        "color-sidebar-background": "#282a36",
        "color-sidebar-item-background--hover": "#44475a",
        "color-sidebar-item-expander-background--hover": "#6272a4",
        "color-sidebar-search-background": "#44475a",
        "color-sidebar-search-background--focus": "#44475a",
    },
    "sidebar_hide_name": True,
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/LLAMATOR-Core/llamator",
            "html": """
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
            """,
            "class": "",
        },
    ],
    "source_repository": "https://github.com/LLAMATOR-Core/llamator",
    "source_branch": "release",
    "source_directory": "src/",
}

autosectionlabel_prefix_document = True

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    "scipy": ("https://docs.scipy.org/doc/scipy/reference/", None),
    "numpy": ("https://numpy.org/doc/stable", None),
}

# Configuration for Napoleon extension
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

add_module_names = False
autodoc_typehints = 'both'

source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'markdown',
    '.md': 'markdown',
}

pygments_style = "dracula"
pygments_dark_style = "dracula"