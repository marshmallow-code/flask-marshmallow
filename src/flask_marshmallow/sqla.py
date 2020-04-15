# -*- coding: utf-8 -*-
"""
    flask_marshmallow.sqla
    ~~~~~~~~~~~~~~~~~~~~~~

    Integration with Flask-SQLAlchemy and marshmallow-sqlalchemy. Provides
    `ModelSchema <marshmallow_sqlalchemy.ModelSchema>` classes that use the scoped session
    from Flask-SQLALchemy.
"""
import sys
from types import ModuleType

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


class SchemaOpts(FlaskSQLAlchemyOptsMixin, msqla.ModelSchemaOpts):
    """Schema options for `~flask_marshmallow.sqla.ModelSchema`.
    Same as `marshmallow_sqlalchemy.SchemaOpts`, except that we add a
    placeholder `DummySession` if ``sqla_session`` is not defined on
    class Meta. The actual session from `flask_sqlalchemy` gets bound
    in `flask_marshmallow.Marshmallow.init_app`.
    """

    pass


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


# Avoid spurious depreciation warnings by delaying the subclassing of
# ModelSchema and TableSchema so that the __init_subclass__ hook isn't
# triggered unless either are accessed.


def _make_model_schema():
    class ModelSchema(msqla.ModelSchema, Schema):
        """ModelSchema that generates fields based on the
        `model` class Meta option, which should be a
        ``db.Model`` class from `flask_sqlalchemy`. Uses the
        scoped session from Flask-SQLAlchemy by default.

        See `marshmallow_sqlalchemy.ModelSchema` for more details
        on the `ModelSchema` API.
        """

        OPTIONS_CLASS = SchemaOpts

    return ModelSchema


def _make_table_schema():
    class TableSchema(msqla.TableSchema, Schema):
        """TableSchema that generates fields based on the
        `table` class Meta option, which should be a
        ``Table`` object from SQLAlchemy.
        Example: ::

            class UserSchema(ma.TableSchema):
                class Meta:
                    table = models.User.__table__

        See `marshmallow_sqlalchemy.TableSchema` for more details
        on the `TableSchema` API.
        """

    return TableSchema


if sys.version_info >= (3, 7):

    def __getattr__(name):
        if name == "ModelSchema":
            return _make_model_schema()

        if name == "TableSchema":
            return _make_table_schema()

        raise AttributeError("module {} has no attribute {}".format(__name__, name))


else:

    class module(ModuleType):
        DummySession = DummySession
        FlaskSQLAlchemyOptsMixin = FlaskSQLAlchemyOptsMixin
        SchemaOpts = SchemaOpts
        SQLAlchemySchema = SQLAlchemySchema
        SQLAlchemyAutoSchema = SQLAlchemyAutoSchema
        auto_field = staticmethod(auto_field)
        HyperlinkRelated = HyperlinkRelated

        def __getattr__(self, name):
            if name == "ModelSchema":
                return _make_model_schema()

            if name == "TableSchema":
                return _make_table_schema()

            raise AttributeError("module {} has no attribute {}".format(__name__, name))

    # keep ref to module so can continue to access globals.
    old_module = sys.modules[__name__]
    # overwrite module with class so can use __getattr__()
    new_module = sys.modules[__name__] = module(__name__)
    # make new module look like old one
    new_module.__dict__.update({"__file__": __file__, "__doc__": __doc__})
