# -*- coding: utf-8 -*-
"""
    flask_marshmallow
    ~~~~~~~~~~~~~~~~~

    Integrates the marshmallow serialization/deserialization library
    with your Flask application.

    :copyright: (c) 2014 by Steven Loria
    :license: MIT, see LICENSE for more details.
"""
import warnings

from flask import jsonify
from marshmallow import (
    Schema as BaseSchema,
    fields as base_fields,
    exceptions,
    pprint
)
from . import fields

__version__ = '0.5.0'
__author__ = 'Steven Loria'
__license__ = 'MIT'

__all__ = [
    'EXTENSION_NAME',
    'Marshmallow',
    'Schema',
    'fields',
    'exceptions',
    'pprint'
]

EXTENSION_NAME = 'flask-marshmallow'

def _attach_fields(obj):
    """Attach all the marshmallow fields classes to ``obj``, including
    Flask-Marshmallow's custom fields.
    """
    for attr in base_fields.__all__:
        if not hasattr(obj, attr):
            setattr(obj, attr, getattr(base_fields, attr))
    for attr in fields.__all__:
        setattr(obj, attr, getattr(fields, attr))


class Schema(BaseSchema):
    """Base serializer with which to define custom serializers.

    http://marshmallow.readthedocs.org/en/latest/api_reference.html#serializer
    """

    def jsonify(self, *args, **kwargs):
        """Return a JSON response of the serialized data.

        .. deprecated:: 0.4.0
        """
        warnings.warn(
            'Schema.jsonify is deprecated. Call jsonify on the '
            'output of Schema.dump instead.',
            category=DeprecationWarning
        )
        return jsonify(self.data, *args, **kwargs)

class Marshmallow(object):
    """Wrapper class that integrates Marshmallow with a Flask application.

    To use it, instantiate with an application::

        app = Flask(__name__)
        ma = Marshmallow(app)

    The object provides access to the :class:`Schema` class,
    all fields in :mod:`marshmallow.fields`, as well as the Flask-specific
    fields in :mod:`flask_marshmallow.fields`.

    You can declare schema like so::

        class BookSchema(ma.Schema):
            class Meta:
                fields = ('id', 'title', 'author', 'links')

            author = ma.Nested(AuthorMarshal)

            links = ma.Hyperlinks({
                'self': ma.URLFor('book_detail', id='<id>'),
                'collection': ma.URLFor('book_list')
            })

    :param Flask app: The Flask application object.
    """

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

        self.Schema = Schema
        _attach_fields(self)

    def init_app(self, app):
        """Initializes the application with the extension.

        :param Flask app: The Flask application object.
        """
        if app.config.get('MARSHMALLOW_DATEFORMAT'):
            warnings.warn(
                'The MARSHMALLOW_DATEFORMAT config value has been removed. '
                'Use a base Schema class instead.',
                category=UserWarning
            )
        if app.config.get('MARSHMALLOW_STRICT'):
            warnings.warn(
                'The MARSHMALLOW_STRICT config value has been removed. '
                'Use a base Schema class instead.',
                category=UserWarning
            )
        app.config.setdefault('MARSHMALLOW_DATEFORMAT', 'iso')
        app.config.setdefault('MARSHMALLOW_STRICT', False)
        app.extensions = getattr(app, 'extensions', {})
        app.extensions[EXTENSION_NAME] = self
