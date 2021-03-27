"""
    flask_marshmallow.fields
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Custom, Flask-specific fields.

    See the `marshmallow.fields` module for the list of all fields available from the
    marshmallow library.
"""
import copy
import typing
import re

from flask import current_app, url_for
from marshmallow import fields
from marshmallow import missing


__all__ = [
    "URLFor",
    "UrlFor",
    "AbsoluteURLFor",
    "AbsoluteUrlFor",
    "Hyperlinks",
    "FlaskConfig",
]


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
    object to be serialized, and ``**values`` should be passed to the ``values``
    parameter.

    Usage: ::

        url = URLFor('author_get', values=dict(id='<id>'))
        https_url = URLFor('author_get', values=dict(id='<id>', _scheme='https', _external=True))

    :param str endpoint: Flask endpoint name.
    :param dict values: Same keyword arguments as Flask's url_for, except string
        arguments enclosed in `< >` will be interpreted as attributes to pull
        from the object.
    :param kwargs: keyword arguments to pass to marshmallow field (e.g. ``required``).
    """

    _CHECK_ATTRIBUTE = False

    def __init__(self, endpoint, values=None, **kwargs):
        self.endpoint = endpoint
        self.values = values or kwargs  # kwargs for backward compatibility
        fields.Field.__init__(self, **kwargs)

    def _serialize(self, value, key, obj):
        """Output the URL for the endpoint, given the kwargs passed to
        ``__init__``.
        """
        param_values = {}
        for name, attr_tpl in self.values.items():
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

    def __init__(self, endpoint, values=None, **kwargs):
        if values:  # for backward compatibility
            values["_external"] = True
        else:
            kwargs["_external"] = True
        URLFor.__init__(self, endpoint=endpoint, values=values, **kwargs)


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
            'self': URLFor('author', values=dict(id='<id>')),
            'collection': URLFor('author_list'),
        })

    `URLFor` objects can be nested within the dictionary. ::

        _links = Hyperlinks({
            'self': {
                'href': URLFor('book', values=dict(id='<id>')),
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


class FlaskConfig(fields.Field):
    """Field that outputs the value of a Flask configuration entry

    Takes a field instance or type to serialise to, and an optional configuration
    name. If the name is not given, the current field name, uppercased, is used:

    Example: ::

        class SomeSchema(Schema):
            # serialize the SESSION_COOKIE_NAME configuration variable, as a
            # string.
            session_cookie_name = FlaskConfig()

            # serialize APPLICATION_ROOT as a string, under the name cookie_path
            cookie_path = FlaskConfig(config_name="APPLICATION_ROOT")

            # serialize the SESSION_COOKIE_HTTPONLY configuration variable,
            # as a boolean flag, using the name 'cookie_httponly'
            cookie_httponly = FlaskConfig(fields.Boolean, "SESSION_COOKIE_HTTPONLY")

    .. warning::
        Deserialisation with ``dump_only=False`` doesn't handle partial updates of nested
        datastructures; a ``FlaskConfig(Nested(OtherSchema, only=["name"]),
        dump_only=False)`` field will replace the Flask configuration value entirely, not
        just the ``name`` field.

    :param marshmallow.fields.Field cls_or_instance: A field class or instance.
        If ``None``, defaults to :class:`marshmallow.fields.String`.
    :param str config_name: The name of the :ref:`Flask config variable <flask:config>`
        to serialize. If ``None``, the name of the field converted to uppercase will be
        used.
    :param bool dump_only: By default, FlaskConfig fields are "read-only" fields. Set
        this option to ``False`` to automatically update the flask configuration when
        deserialising.
    :param kwargs: The same keyword arguments that :class:`marshmallow.fields.Field`
        receives.

    """

    _CHECK_ATTRIBUTE = False

    def __init__(
        self,
        cls_or_instance: typing.Union[fields.Field, type] = fields.String,
        config_name: typing.Optional[str] = None,
        dump_only: bool = True,
        **kwargs
    ) -> None:
        super().__init__(dump_only=dump_only, **kwargs)
        try:
            self.inner = fields.resolve_field_instance(cls_or_instance)
        except fields.FieldInstanceResolutionError as error:
            raise ValueError(
                "The Flask config field must be a subclass or instance of "
                "marshmallow.base.FieldABC."
            ) from error
        if isinstance(self.inner, fields.Nested):
            self.only = self.inner.only
            self.exclude = self.inner.exclude
        self.config_name = config_name

    def _bind_to_schema(self, field_name, schema):
        super()._bind_to_schema(field_name, schema)
        if self.config_name is None:
            self.config_name = field_name.upper()
        self.inner = copy.deepcopy(self.inner)
        self.inner._bind_to_schema(field_name, self)
        if isinstance(self.inner, fields.Nested):
            self.inner.only = self.only
            self.inner.exclude = self.exclude

    def _serialize(self, value, *args, **kwargs) -> typing.Optional[typing.Any]:
        value = current_app.config[self.config_name]
        return self.inner._serialize(value, *args, **kwargs)

    def _deserialize(self, value, *args, **kwargs) -> typing.Any:
        current_app.config[self.config_name] = self.inner.deserialize(
            value, *args, **kwargs
        )
        return missing
