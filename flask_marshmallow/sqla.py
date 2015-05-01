# -*- coding: utf-8 -*-
"""Integration with Flask-SQLAlchemy and marshmallow-sqlalchemy."""

import marshmallow_sqlalchemy as msqla
from .schema import Schema

class DummySession(object):
    """Placeholder session object."""
    pass

class SchemaOpts(msqla.SchemaOpts):
    """Schema options for `ModelSchema <flask_marshmallow.sqla.ModelSchema>`.
    Same as `marshmallow_sqlalchemy.SchemaOpts`, except that we add a
    placeholder `DummySession` if ``sqla_session`` is not defined on
    class Meta. The actual session from `flask_sqlalchemy` gets bound
    in `init_app`.
    """
    session = DummySession()

    def __init__(self, meta):
        if not hasattr(meta, 'sqla_session'):
            meta.sqla_session = self.session
        super(SchemaOpts, self).__init__(meta)

class ModelSchema(msqla.ModelSchema, Schema):
    """ModelSchema that generates fields based on the
    `model` class Meta option, which should be a
    ``db.Model`` class from `flask_sqlalchemy`. Uses the
    scoped session from Flask-SQLAlchemy by default.

    See `marshmallow_sqlalchemy.ModelSchema` for more details
    on the `ModelSchema` API.
    """
    OPTIONS_CLASS = SchemaOpts
