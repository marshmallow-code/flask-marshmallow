# -*- coding: utf-8 -*-
import json
from flask import Flask, url_for
from werkzeug.wrappers import BaseResponse
from flask_marshmallow import Marshmallow

from tests.markers import flask_1_req

def test_deferred_initialization():
    app = Flask(__name__)
    m = Marshmallow()
    m.init_app(app)

    assert 'flask-marshmallow' in app.extensions

def test_schema(app, schemas, mockauthor):
    s = schemas.AuthorSchema()
    result = s.dump(mockauthor)
    assert result.data['id'] == mockauthor.id
    assert result.data['name'] == mockauthor.name
    assert result.data['absolute_url'] == url_for('author',
        id=mockauthor.id, _external=True)
    links = result.data['links']
    assert links['self'] == url_for('author', id=mockauthor.id)
    assert links['collection'] == url_for('authors')

def test_jsonify_instance(app, schemas, mockauthor):
    s = schemas.AuthorSchema()
    resp = s.jsonify(mockauthor)
    assert isinstance(resp, BaseResponse)
    assert resp.content_type == 'application/json'
    obj = json.loads(resp.get_data(as_text=True))
    assert isinstance(obj, dict)

@flask_1_req
def test_jsonify_collection(app, schemas, mockauthorlist):
    s = schemas.AuthorSchema()
    resp = s.jsonify(mockauthorlist, many=True)
    assert isinstance(resp, BaseResponse)
    assert resp.content_type == 'application/json'
    obj = json.loads(resp.get_data(as_text=True))
    assert isinstance(obj, list)

def test_links_within_nested_object(app, schemas, mockbook):
    s = schemas.BookSchema()
    result = s.dump(mockbook)
    assert result.data['title'] == mockbook.title
    author = result.data['author']
    assert author['links']['self'] == url_for('author', id=mockbook.author.id)
    assert author['links']['collection'] == url_for('authors')
