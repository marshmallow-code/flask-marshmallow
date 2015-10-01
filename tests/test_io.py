# -*- coding: utf-8 -*-
from flask_marshmallow import marshal_with, use_schema
from webtest import TestApp

from tests.conftest import Author

def test_marshal_with(app, schemas):
    url = '/marshal_with/author'

    schema = schemas.AuthorSchema(exclude=('links', 'absolute_url'))

    @app.route(url)
    @marshal_with(schema)
    def author_detail():
        return Author(id=42, name='Sun Tzu')

    client = TestApp(app)
    res = client.get(url)
    assert res.status_code == 200
    assert res.json == schema.dump(Author(id=42, name='Sun Tzu')).data


def test_use_schema(app, schemas):
    url = '/use_schema/author'
    schema = schemas.AuthorSchema(exclude=('links', 'absolute_url'))

    @app.route(url, methods=['POST'])
    @use_schema(schema)
    def author_create(reqargs):
        return Author(**reqargs)

    client = TestApp(app)
    res = client.post(url, {'id': 42, 'name': 'Sun Tzu'})
    assert res.json == schema.dump(Author(id=42, name='Sun Tzu')).data
