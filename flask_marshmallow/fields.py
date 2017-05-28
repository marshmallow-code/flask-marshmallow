# -*- coding: utf-8 -*-
"""
    flask_marshmallow.fields
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Custom, Flask-specific fields.

    See the `marshmallow.fields` module for the list of all fields available from the
    marshmallow library.
"""
import re

from flask import url_for
from marshmallow import fields
from marshmallow.compat import iteritems
from marshmallow import missing

from .compat import get_value


_tpl_pattern = re.compile(r'\s*<\s*(\S*)\s*>\s*')

__all__ = [
    'URLFor',
    'UrlFor',
    'AbsoluteURLFor',
    'AbsoluteUrlFor',
    'Hyperlinks',
]

def _tpl(val):
    """Return value within ``< >`` if possible, else return ``None``."""
    match = _tpl_pattern.match(val)
    if match:
        return match.groups()[0]
    return None


class URLFor(fields.Field):
    """Field that outputs the URL for an endpoint. Acts identically to
    Flask's ``url_for`` function, except that arguments can be pulled from the
    object to be serialized.

    Usage: ::

        url = URLFor('author_get', id='<id>')
        https_url = URLFor('author_get', id='<id>', _scheme='https', _external=True)

    :param str endpoint: Flask endpoint name.
    :param kwargs: Same keyword arguments as Flask's url_for, except string
        arguments enclosed in `< >` will be interpreted as attributes to pull
        from the object.
    """
    _CHECK_ATTRIBUTE = False

    def __init__(self, endpoint, **kwargs):
        self.endpoint = endpoint
        self.params = kwargs
        fields.Field.__init__(self, **kwargs)

    def _format(self, val):
        return val

    def _serialize(self, value, key, obj):
        """Output the URL for the endpoint, given the kwargs passed to
        ``__init__``.
        """
        param_values = {}
        for name, attr_tpl in iteritems(self.params):
            attr_name = _tpl(str(attr_tpl))
            if attr_name:
                attribute_value = get_value(obj, attr_name, default=missing)
                if attribute_value is not missing:
                    param_values[name] = attribute_value
                else:
                    raise AttributeError(
                        '{attr_name!r} is not a valid '
                        'attribute of {obj!r}'.format(attr_name=attr_name, obj=obj)
                    )
            else:
                param_values[name] = attr_tpl
        return url_for(self.endpoint, **param_values)

UrlFor = URLFor


class AbsoluteURLFor(URLFor):
    """Field that outputs the absolute URL for an endpoint."""

    def __init__(self, endpoint, **kwargs):
        kwargs['_external'] = True
        URLFor.__init__(self, endpoint=endpoint, **kwargs)

    def _format(self, val):
        return val

AbsoluteUrlFor = AbsoluteURLFor


def _rapply(d, func, *args, **kwargs):
    """Apply a function to all values in a dictionary or list of dictionaries, recursively."""
    if isinstance(d, (tuple, list)):
        return [_rapply(each, func, *args, **kwargs) for each in d]
    if isinstance(d, dict):
        return {
            key: _rapply(value, func, *args, **kwargs)
            for key, value in iteritems(d)
        }
    else:
        return func(d, *args, **kwargs)


def _url_val(val, key, obj, **kwargs):
    """Function applied by `HyperlinksField` to get the correct value in the
    schema.
    """
    if isinstance(val, URLFor):
        return val.serialize(key, obj, **kwargs)
    else:
        return val


class Hyperlinks(fields.Field):
    """Field that outputs a dictionary of hyperlinks,
    given a dictionary schema with :class:`~flask_marshmallow.fields.URLFor`
    objects as values.

    Example: ::

        _links = Hyperlinks({
            'self': URLFor('author', id='<id>'),
            'collection': URLFor('author_list'),
            }
        })

    `URLFor` objects can be nested within the dictionary. ::

        _links = Hyperlinks({
            'self': {
                'href': URLFor('book', id='<id>'),
                'title': 'book detail'
            }
        })

    :param dict schema: A dict that maps names to
        :class:`~flask_marshmallow.fields.URLFor` fields.
    """
    _CHECK_ATTRIBUTE = False

    def __init__(self, schema, **kwargs):
        self.schema = schema
        fields.Field.__init__(self, **kwargs)

    def _format(self, val):
        return val

    def _serialize(self, value, attr, obj):
        return _rapply(self.schema, _url_val, key=attr, obj=obj)
