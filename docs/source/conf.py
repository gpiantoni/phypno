#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os import chdir
from os.path import abspath, dirname, join
from datetime import datetime
now = datetime.now()

# make sure that we're in the source directory
# so that it's consistent between read the docs and local
cur_dir = abspath(dirname(__file__))

import phypno

# -- General configuration ------------------------------------------------
extensions = [
    'sphinx.ext.autosummary',
    'sphinx.ext.autodoc',
    'sphinx.ext.githubpages',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
    ]

# autodoc options
autosummary_generate = True
autodoc_default_flags = ['private-members']

# Napoleon settings
napoleon_use_rtype = False

# todo settings
todo_include_todos = True
todo_link_only = True

# source suffix
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'phypno'
copyright = '2013-{}, Gio Piantoni'.format(now.year)
author = 'Gio Piantoni'

# The short X.Y version.
version = phypno.__version__
# The full version, including alpha/beta/rc tags.
release = version

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.

html_theme = 'sphinx_rtd_theme'

html_show_sphinx = False

# Output file base name for HTML help builder.
htmlhelp_basename = 'phypnodoc'


def run_apidoc(_):
    chdir(cur_dir)  # use same dir as readthedocs, which is docs/source
    from sphinx.apidoc import main
    output_path = join(cur_dir, 'api')
    # here use paths relative to docs/source
    main(['', '-f', '-e', '--module-first', '-o', output_path, '../../phypno',
          '../../phypno/viz'])

def setup(app):
    app.connect('builder-inited', run_apidoc)
