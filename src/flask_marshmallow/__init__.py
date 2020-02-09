# -*- coding: utf-8 -*-
"""
    flask_marshmallow
    ~~~~~~~~~~~~~~~~~

    Integrates the marshmallow serialization/deserialization library
    with your Flask application.
"""
import warnings
from distutils.version import LooseVersion

from marshmallow import fields as base_fields, exceptions, pprint

from . import fields
from .schema import Schema

has_sqla = False
try:
    import flask_sqlalchemy  # noqa: F401
except ImportError:
    has_sqla = False
else:
    try:
        from . import sqla
    except ImportError:
        warnings.warn(
            "Flask-SQLAlchemy integration requires "
            "marshmallow-sqlalchemy to be installed."
        )
    else:
        has_sqla = True

__version__ = "0.11.0"
__version_info__ = tuple(LooseVersion(__version__).version)
__all__ = ["EXTENSION_NAME", "Marshmallow", "Schema", "fields", "exceptions", "pprint"]

EXTENSION_NAME = "flask-marshmallow"


def _attach_fields(obj):
    """Attach all the marshmallow fields classes to ``obj``, including
    Flask-Marshmallow's custom fields.
    """
    for attr in base_fields.__all__:
        if not hasattr(obj, attr):
            setattr(obj, attr, getattr(base_fields, attr))
    for attr in fields.__all__:
        setattr(obj, attr, getattr(fields, attr))


class Marshmallow(object):
    """Wrapper class that integrates Marshmallow with a Flask application.

    To use it, instantiate with an application::

        from flask import Flask

        app = Flask(__name__)
        ma = Marshmallow(app)

    The object provides access to the :class:`Schema` class,
    all fields in :mod:`marshmallow.fields`, as well as the Flask-specific
    fields in :mod:`flask_marshmallow.fields`.

    You can declare schema like so::

        class BookSchema(ma.Schema):
            class Meta:
                fields = ('id', 'title', 'author', 'links')

            author = ma.Nested(AuthorSchema)

            links = ma.Hyperlinks({
                'self': ma.URLFor('book_detail', id='<id>'),
                'collection': ma.URLFor('book_list')
            })


    In order to integrate with Flask-SQLAlchemy, this extension must be initialized *after*
    `flask_sqlalchemy.SQLAlchemy`. ::

            db = SQLAlchemy(app)
            ma = Marshmallow(app)

    This gives you access to `ma.SQLAlchemySchema` and `ma.SQLAlchemyAutoSchema`, which generate
    marshmallow `~marshmallow.Schema` classes based on the passed in model or table. ::

        class AuthorSchema(ma.SQLAlchemyAutoSchema):
            class Meta:
                model = Author

    :param Flask app: The Flask application object.
    """

    def __init__(self, app=None):
        self.Schema = Schema
        if has_sqla:
            self.ModelSchema = sqla.ModelSchema
            self.TableSchema = sqla.TableSchema
            self.SQLAlchemySchema = sqla.SQLAlchemySchema
            self.SQLAlchemyAutoSchema = sqla.SQLAlchemyAutoSchema
            self.auto_field = sqla.auto_field
            self.HyperlinkRelated = sqla.HyperlinkRelated
        _attach_fields(self)
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initializes the application with the extension.

        :param Flask app: The Flask application object.
        """
        app.extensions = getattr(app, "extensions", {})

        # If using Flask-SQLAlchemy, attach db.session to ModelSchema
        if has_sqla and "sqlalchemy" in app.extensions:
            db = app.extensions["sqlalchemy"].db
            self.ModelSchema.OPTIONS_CLASS.session = db.session
        app.extensions[EXTENSION_NAME] = self
