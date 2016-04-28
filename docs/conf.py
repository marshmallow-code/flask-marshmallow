# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, os.path.abspath('..'))
import flask_marshmallow
sys.path.append(os.path.abspath("_themes"))
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx_issues'
]

intersphinx_mapping = {
    'python': ('http://python.readthedocs.io/en/latest/', None),
    'flask': ('http://flask.pocoo.org/docs/latest/', None),
    'flask-sqlalchemy': ('http://flask-sqlalchemy.pocoo.org/latest/', None),
    'marshmallow': ('http://marshmallow.readthedocs.io/en/latest/', None),
    'marshmallow-sqlalchemy': ('http://marshmallow-sqlalchemy.readthedocs.io/en/latest/', None),
}

primary_domain = 'py'
default_role = 'py:obj'

issues_github_path = 'marshmallow-code/flask-marshmallow'

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'
# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'Flask-Marshmallow'
copyright = u'2014-2016'

version = release = flask_marshmallow.__version__
exclude_patterns = ['_build']
# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'flask_theme_support.FlaskyStyle'
html_theme = 'flask_small'
html_theme_path = ['_themes']
html_static_path = ['_static']
html_sidebars = {
    'index': ['side-primary.html', 'searchbox.html'],
    '**': ['side-secondary.html', 'localtoc.html',
                 'relations.html', 'searchbox.html']
}

htmlhelp_basename = 'flask-marshmallowdoc'
