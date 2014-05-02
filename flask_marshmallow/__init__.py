# -*- coding: utf-8 -*-
"""
    flask.ext.marshmallow
    ~~~~~~~~~~~~~~~~~

    Adds support for the marshmallow serialization library to your application.

    :copyright: (c) 2014 by Steven Loria
    :license: MIT, see LICENSE for more details.
"""

from flask import jsonify, current_app, json
from marshmallow import (
    Serializer as BaseSerializer,
    fields as base_fields,
    exceptions,
    pprint
)
from marshmallow.serializer import SerializerOpts as BaseSerializerOpts
from . import fields

__version__ = '0.1.0'
__author__ = 'Steven Loria'
__license__ = 'MIT'
__all__ = [
    'EXTENSION_NAME',
    'SerializerOpts',
    'Marshmallow',
    'Serializer',
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

class SerializerOpts(BaseSerializerOpts):
    """``class Meta`` options for the Serializer. Defines defaults, pulling
    values from the current Flask app's config where appropriate.
    """

    def __init__(self, meta):
        BaseSerializerOpts.__init__(self, meta)
        # Use current app's config as defaults
        self.strict = getattr(
            meta, 'strict', current_app.config['MARSHMALLOW_STRICT']
        )
        self.dateformat = getattr(
            meta, 'dateformat', current_app.config['MARSHMALLOW_DATEFORMAT']
        )


class Serializer(BaseSerializer):
    """Base serializer with which to define custom serializers.

    http://marshmallow.readthedocs.org/en/latest/api_reference.html#serializer
    """

    OPTIONS_CLASS = SerializerOpts

    def jsonify(self, *args, **kwargs):
        """Return a JSON response of the serialized data."""
        return jsonify(self.data, *args, **kwargs)

class Marshmallow(object):

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

        self.Serializer = Serializer
        _attach_fields(self)

    def init_app(self, app):
        """Initializes the application with the extension.

        :param Flask app: The Flask application object.
        """
        app.config.setdefault('MARSHMALLOW_DATEFORMAT', 'rfc')
        app.config.setdefault('MARSHMALLOW_STRICT', False)
        app.extensions = getattr(app, 'extensions', {})
        app.extensions[EXTENSION_NAME] = self
