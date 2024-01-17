import json

from flask import Flask, url_for
from werkzeug.wrappers import Response

from flask_marshmallow import Marshmallow


def test_deferred_initialization():
    app = Flask(__name__)
    m = Marshmallow()
    m.init_app(app)

    assert "flask-marshmallow" in app.extensions


def test_schema(app, schemas, mockauthor):
    s = schemas.AuthorSchema()
    result = s.dump(mockauthor)
    assert result["id"] == mockauthor.id
    assert result["name"] == mockauthor.name
    assert result["absolute_url"] == url_for("author", id=mockauthor.id, _external=True)
    links = result["links"]
    assert links["self"] == url_for("author", id=mockauthor.id)
    assert links["collection"] == url_for("authors")


def test_jsonify_instance(app, schemas, mockauthor):
    s = schemas.AuthorSchema()
    resp = s.jsonify(mockauthor)
    assert isinstance(resp, Response)
    assert resp.content_type == "application/json"
    obj = json.loads(resp.get_data(as_text=True))
    assert isinstance(obj, dict)


def test_jsonify_collection(app, schemas, mockauthorlist):
    s = schemas.AuthorSchema()
    resp = s.jsonify(mockauthorlist, many=True)
    assert isinstance(resp, Response)
    assert resp.content_type == "application/json"
    obj = json.loads(resp.get_data(as_text=True))
    assert isinstance(obj, list)


def test_jsonify_collection_via_schema_attr(app, schemas, mockauthorlist):
    s = schemas.AuthorSchema(many=True)
    resp = s.jsonify(mockauthorlist)
    assert isinstance(resp, Response)
    assert resp.content_type == "application/json"
    obj = json.loads(resp.get_data(as_text=True))
    assert isinstance(obj, list)


def test_links_within_nested_object(app, schemas, mockbook):
    s = schemas.BookSchema()
    result = s.dump(mockbook)
    assert result["title"] == mockbook.title
    author = result["author"]
    assert author["links"]["self"] == url_for("author", id=mockbook.author.id)
    assert author["links"]["collection"] == url_for("authors")
