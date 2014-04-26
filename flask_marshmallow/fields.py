
# -*- coding: utf-8 -*-
"""
    flask_marshmallow.fields
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Field classes for formatting and validating the serialized object.

    All marshmallow fields are importable from this module.

    See http://marshmallow.readthedocs.org/en/latest/api_reference.html#module-marshmallow.fields
"""
import re
import sys

from marshmallow import fields
# Make all marshmallow fields importable from flask_marshmallow.fields
# flask8: noqa
from marshmallow.fields import *
from flask import url_for

# Py2/3 compatibility
PY2 = sys.version_info[0] == 2
if not PY2:
    iteritems = lambda d: iter(d.items())
else:
    iteritems = lambda d: d.iteritems()

_tpl_pattern = re.compile(r'\s*<\s*(\S*)\s*>\s*')


def _tpl(val):
    """Return value within ``< >`` if possible, else return ``None``."""
    match = _tpl_pattern.match(val)
    if match:
        return match.groups()[0]
    return None


class URL(fields.Raw):
    """Field that outputs the URL for an endpoint. Acts identically to
    Flask's ``url_for`` function, except that arguments can be pulled from the
    object to be serialized.

    Usage: ::

        url = URL('author_get', id='<id>')
        https_url = URL('author_get', id='<id>', _scheme='https', _external=True)

    :param str endpoint: Flask endpoint name.
    :param kwargs: Same keyword arguments as Flask's url_for, except string
        arguments enclosed in `< >` will be interpreted as attributes to pull
        from the object.
    """

    def __init__(self, endpoint, **kwargs):
        self.endpoint = endpoint
        self.params = kwargs
        # All fields need self.attribute
        self.attribute = None
        self.required = False

    def format(self, val):
        return val

    def output(self, key, obj):
        """Output the URL for the endpoint, given the kwargs passed to
        ``__init__``.
        """
        param_values = {}
        for name, attr in iteritems(self.params):
            attr_name = _tpl(str(attr))
            if attr_name:
                attribute_value = self.get_value(key=attr_name, obj=obj)
                if attribute_value:
                    param_values[name] = attribute_value
                else:
                    raise AttributeError(
                        '{attr_name!r} is not a valid '
                        'attribute of {obj!r}'.format(
                            attr_name=attr_name, obj=obj,
                        ))
            else:
                param_values[name] = attr
        return url_for(self.endpoint, **param_values)

Url = URL


class AbsoluteURL(URL):
    """Field that outputs the absolute URL for an endpoint."""

    def __init__(self, endpoint, **kwargs):
        kwargs['_external'] = True
        URL.__init__(self, endpoint=endpoint, **kwargs)

    def format(self, val):
        return val

AbsoluteUrl = AbsoluteURL


def _rapply(d, func, *args, **kwargs):
    """Apply a function to all values in a dictionary, recursively."""
    if isinstance(d, dict):
        return {
            key: _rapply(value, func, *args, **kwargs)
            for key, value in iteritems(d)
        }
    else:
        return func(d, *args, **kwargs)


def _url_val(val, key, obj, **kwargs):
    """Function applied by ``HyperlinksField`` to get the correct value in the
    schema.
    """
    if isinstance(val, URL):
        return val.output(key, obj, **kwargs)
    else:
        return val


class Hyperlinks(fields.Raw):
    """Field that outputs a dictionary of hyperlinks,
    given a dictionary schema with :class:`URL <flask_marshmallow.fields.URL>`
    objects as values.

    Example: ::

        _links = Hyperlinks({
            'self': URL('author', id='<id>'),
            'collection': URL('author_list'),
            }
        })

    ``URL`` objects can be nested within the dictionary. ::

        _links = Hyperlinks({
            'self': {
                'href': URL('book', id='<id>'),
                'title': 'book detail'
            }
        })

    :param dict schema: A dict that maps names to
        :class:`URL <flask_marshmallow.fields.URL>` endpoints.
    """

    def __init__(self, schema):
        self.schema = schema
        self.attribute = None
        self.required = False

    def format(self, val):
        return val

    def output(self, key, obj):
        return _rapply(self.schema, _url_val, key=key, obj=obj)
