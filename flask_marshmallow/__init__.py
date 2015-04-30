# -*- coding: utf-8 -*-
"""
    flask_marshmallow
    ~~~~~~~~~~~~~~~~~

    Integrates the marshmallow serialization/deserialization library
    with your Flask application.

    :copyright: (c) 2014-2015 by Steven Loria
    :license: MIT, see LICENSE for more details.
"""

from flask import jsonify
from marshmallow import (
    Schema as BaseSchema,
    fields as base_fields,
    exceptions,
    pprint
)
from . import fields

try:
    import flask_sqlalchemy  # flake8: noqa
    from . import sqla
except ImportError:
    has_sqla = False
else:
    has_sqla = True

__version__ = '0.6.0.dev'
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

    def jsonify(self, obj, many=False, *args, **kwargs):
        """Return a JSON response containing the serialized data.


        :param obj: Object to serialize.
        :param bool many: Set to `True` if `obj` should be serialized as a collection.
        :param kwargs: Additional keyword arguments passed to `flask.jsonify`.

        .. versionchanged:: 0.6.0
            Takes the same arguments as `marshmallow.Schema.dump`. Additional
            keyword arguments are passed to `flask.jsonify`.
        """
        data = self.dump(obj, many=many).data
        return jsonify(data, *args, **kwargs)

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
        self.Schema = Schema
        if has_sqla:
            self.ModelSchema = sqla.ModelSchema
        _attach_fields(self)
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initializes the application with the extension.

        :param Flask app: The Flask application object.
        """
        app.extensions = getattr(app, 'extensions', {})

        if has_sqla and 'sqlalchemy' in app.extensions:
            db = app.extensions['sqlalchemy'].db
            self.ModelSchema.Meta.sqla_session = db.session
        app.extensions[EXTENSION_NAME] = self
