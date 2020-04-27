# -*- coding: utf-8 -*-
"""
    flask_marshmallow.sqla
    ~~~~~~~~~~~~~~~~~~~~~~

    Integration with Flask-SQLAlchemy and marshmallow-sqlalchemy. Provides
    `SQLAlchemySchema <marshmallow_sqlalchemy.SQLAlchemySchema>` and
    `SQLAlchemyAutoSchema <marshmallow_sqlalchemy.SQLAlchemyAutoSchema>` classes
    that use the scoped session from Flask-SQLAlchemy.
"""
from flask import url_for, current_app
from six.moves.urllib import parse
import marshmallow_sqlalchemy as msqla
from marshmallow.exceptions import ValidationError

from .schema import Schema


class DummySession(object):
    """Placeholder session object."""

    pass


class FlaskSQLAlchemyOptsMixin(object):
    session = DummySession()

    def __init__(self, meta, **kwargs):
        if not hasattr(meta, "sqla_session"):
            meta.sqla_session = self.session
        super(FlaskSQLAlchemyOptsMixin, self).__init__(meta, **kwargs)


# SQLAlchemySchema and SQLAlchemyAutoSchema are available in newer ma-sqla versions
if hasattr(msqla, "SQLAlchemySchema"):

    class SQLAlchemySchemaOpts(FlaskSQLAlchemyOptsMixin, msqla.SQLAlchemySchemaOpts):
        pass

    class SQLAlchemySchema(msqla.SQLAlchemySchema, Schema):
        """SQLAlchemySchema that associates a schema with a model via the
        `model` class Meta option, which should be a
        ``db.Model`` class from `flask_sqlalchemy`. Uses the
        scoped session from Flask-SQLAlchemy by default.

        See `marshmallow_sqlalchemy.SQLAlchemySchema` for more details
        on the `SQLAlchemySchema` API.
        """

        OPTIONS_CLASS = SQLAlchemySchemaOpts


else:
    SQLAlchemySchema = None

if hasattr(msqla, "SQLAlchemyAutoSchema"):

    class SQLAlchemyAutoSchemaOpts(
        FlaskSQLAlchemyOptsMixin, msqla.SQLAlchemyAutoSchemaOpts
    ):
        pass

    class SQLAlchemyAutoSchema(msqla.SQLAlchemyAutoSchema, Schema):
        """SQLAlchemyAutoSchema that automatically generates marshmallow fields
        from a SQLAlchemy model's or table's column.
        Uses the scoped session from Flask-SQLAlchemy by default.

        See `marshmallow_sqlalchemy.SQLAlchemyAutoSchema` for more details
        on the `SQLAlchemyAutoSchema` API.
        """

        OPTIONS_CLASS = SQLAlchemyAutoSchemaOpts


else:
    SQLAlchemyAutoSchema = None

auto_field = getattr(msqla, "auto_field", None)


class HyperlinkRelated(msqla.fields.Related):
    """Field that generates hyperlinks to indicate references between models,
    rather than primary keys.

    :param str endpoint: Flask endpoint name for generated hyperlink.
    :param str url_key: The attribute containing the reference's primary
        key. Defaults to "id".
    :param bool external: Set to `True` if absolute URLs should be used,
        instead of relative URLs.
    """

    def __init__(self, endpoint, url_key="id", external=False, **kwargs):
        super(HyperlinkRelated, self).__init__(**kwargs)
        self.endpoint = endpoint
        self.url_key = url_key
        self.external = external

    def _serialize(self, value, attr, obj):
        if value is None:
            return None
        key = super(HyperlinkRelated, self)._serialize(value, attr, obj)
        kwargs = {self.url_key: key}
        return url_for(self.endpoint, _external=self.external, **kwargs)

    def _deserialize(self, value, *args, **kwargs):
        if self.external:
            parsed = parse.urlparse(value)
            value = parsed.path
        endpoint, kwargs = self.adapter.match(value)
        if endpoint != self.endpoint:
            raise ValidationError(
                (
                    'Parsed endpoint "{endpoint}" from URL "{value}"; expected '
                    '"{self.endpoint}"'
                ).format(**locals())
            )
        if self.url_key not in kwargs:
            raise ValidationError(
                'URL pattern "{self.url_key}" not found in {kwargs!r}'.format(
                    **locals()
                )
            )
        return super(HyperlinkRelated, self)._deserialize(
            kwargs[self.url_key], *args, **kwargs
        )

    @property
    def adapter(self):
        return current_app.url_map.bind("")
