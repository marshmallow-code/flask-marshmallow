# -*- coding: utf-8 -*-
"""
    flask_marshmallow
    ~~~~~~~~~~~~~~~~~

    :copyright: (c) 2014 by Steven Loria
    :license: MIT, see LICENSE for more details.
"""


__version__ = '0.1.0'
__author__ = 'Steven Loria'
__license__ = 'MIT'

from flask import jsonify
# flake8: noqa
from marshmallow import Serializer as BaseSerializer, exceptions, pprint
# flake8: noqa
from . import fields

__all__ = ['Serializer', 'fields', 'exceptions', 'pprint']

class Serializer(BaseSerializer):
    """Base serializer with which to define custom serializers.

    http://marshmallow.readthedocs.org/en/latest/api_reference.html#core
    """

    def jsonify(self, *args, **kwargs):
        """Return a JSON response of the serialized data."""
        return jsonify(self.data, *args, **kwargs)
