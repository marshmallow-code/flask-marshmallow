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
from marshmallow import missing


__all__ = ["URLFor", "UrlFor", "AbsoluteURLFor", "AbsoluteUrlFor", "Hyperlinks"]


_tpl_pattern = re.compile(r"\s*<\s*(\S*)\s*>\s*")


def _tpl(val):
    """Return value within ``< >`` if possible, else return ``None``."""
    match = _tpl_pattern.match(val)
    if match:
        return match.groups()[0]
    return None


def _get_value(obj, key, default=missing):
    """Slightly-modified version of marshmallow.utils.get_value.
    If a dot-delimited ``key`` is passed and any attribute in the
    path is `None`, return `None`.
    """
    if "." in key:
        return _get_value_for_keys(obj, key.split("."), default)
    else:
        return _get_value_for_key(obj, key, default)


def _get_value_for_keys(obj, keys, default):
    if len(keys) == 1:
        return _get_value_for_key(obj, keys[0], default)
    else:
        value = _get_value_for_key(obj, keys[0], default)
        # XXX This differs from the marshmallow implementation
        if value is None:
            return None
        return _get_value_for_keys(value, keys[1:], default)


def _get_value_for_key(obj, key, default):
    if not hasattr(obj, "__getitem__"):
        return getattr(obj, key, default)

    try:
        return obj[key]
    except (KeyError, IndexError, TypeError, AttributeError):
        return getattr(obj, key, default)


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

    def _serialize(self, value, key, obj):
        """Output the URL for the endpoint, given the kwargs passed to
        ``__init__``.
        """
        param_values = {}
        for name, attr_tpl in self.params.items():
            attr_name = _tpl(str(attr_tpl))
            if attr_name:
                attribute_value = _get_value(obj, attr_name, default=missing)
                if attribute_value is None:
                    return None
                if attribute_value is not missing:
                    param_values[name] = attribute_value
                else:
                    raise AttributeError(
                        "{attr_name!r} is not a valid "
                        "attribute of {obj!r}".format(attr_name=attr_name, obj=obj)
                    )
            else:
                param_values[name] = attr_tpl
        return url_for(self.endpoint, **param_values)


UrlFor = URLFor


class AbsoluteURLFor(URLFor):
    """Field that outputs the absolute URL for an endpoint."""

    def __init__(self, endpoint, **kwargs):
        kwargs["_external"] = True
        URLFor.__init__(self, endpoint=endpoint, **kwargs)


AbsoluteUrlFor = AbsoluteURLFor


def _rapply(d, func, *args, **kwargs):
    """Apply a function to all values in a dictionary or list of dictionaries, recursively."""
    if isinstance(d, (tuple, list)):
        return [_rapply(each, func, *args, **kwargs) for each in d]
    if isinstance(d, dict):
        return {key: _rapply(value, func, *args, **kwargs) for key, value in d.items()}
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

    def _serialize(self, value, attr, obj):
        return _rapply(self.schema, _url_val, key=attr, obj=obj)
