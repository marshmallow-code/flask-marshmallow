# -*- coding: utf-8 -*-
import mock
import pytest

from flask import Flask, url_for
from werkzeug.routing import BuildError
from werkzeug.wrappers import BaseResponse

from flask.ext.marshmallow import Marshmallow
from flask.ext.marshmallow.fields import _tpl

_app = Flask(__name__)

@_app.route('/author/<int:id>')
def author(id):
    return 'Steven Pressfield'

@_app.route('/authors/')
def authors():
    return 'Steven Pressfield, Chuck Paluhniuk'

@_app.route('/books/')
def books():
    return 'Legend of Bagger Vance, Fight Club'

@_app.route('/books/<id>')
def book(id):
    return 'Legend of Bagger Vance'

mar = Marshmallow(_app)

@pytest.yield_fixture(scope='function')
def app():

    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()

@pytest.fixture(scope='function')
def ma(app):
    return Marshmallow(app)


@pytest.fixture
def mockauthor():
    author = mock.Mock(spec=['id', 'name'])
    author.id = 123
    author.name = 'Fred Douglass'
    return author

@pytest.fixture
def mockbook(mockauthor):
    book = mock.Mock(spec=['id', 'author', 'title'])
    book.id = 42
    book.author = mockauthor
    book.title = 'Legend of Bagger Vance'
    return book


@pytest.mark.parametrize('template', [
    '<id>',
    ' <id>',
    '<id> ',
    '< id>',
    '<id  >',
    '< id >',
])
def test_tpl(template):
    assert _tpl(template) == 'id'
    assert _tpl(template) == 'id'
    assert _tpl(template) == 'id'

def test_url_field(ma, mockauthor):
    field = ma.URLFor('author', id='<id>')
    result = field.serialize('url', mockauthor)
    assert result == url_for('author', id=mockauthor.id)

    mockauthor.id = 0
    result = field.serialize('url', mockauthor)
    assert result == url_for('author', id=0)

def test_url_field_with_invalid_attribute(ma, mockauthor):
    field = ma.URLFor('author', id='<not-an-attr>')
    with pytest.raises(AttributeError) as excinfo:
        field.serialize('url', mockauthor)
    expected_msg = '{0!r} is not a valid attribute of {1!r}'.format(
        'not-an-attr', mockauthor)
    assert expected_msg in str(excinfo)

def test_url_field_deserialization(ma):
    field = ma.URLFor('author', id='<not-an-attr>')
    # noop
    assert field.deserialize('foo') == 'foo'
    assert field.deserialize(None) is None

def test_invalid_endpoint_raises_build_error(ma, mockauthor):
    field = ma.URLFor('badendpoint')
    with pytest.raises(BuildError):
        field.serialize('url', mockauthor)

def test_hyperlinks_field(ma, mockauthor):
    field = ma.Hyperlinks({
        'self': ma.URLFor('author', id='<id>'),
        'collection': ma.URLFor('authors')
    })

    result = field.serialize('_links', mockauthor)
    assert result == {
        'self': url_for('author', id=mockauthor.id),
        'collection': url_for('authors')
    }

def test_hyperlinks_field_recurses(ma, mockauthor):
    field = ma.Hyperlinks({
        'self': {
            'href': ma.URLFor('author', id='<id>'),
            'title': 'The author'
        },
        'collection': {
            'href': ma.URLFor('authors'),
            'title': 'Authors list'
        }
    })
    result = field.serialize('_links', mockauthor)

    assert result == {
        'self': {'href': url_for('author', id=mockauthor.id),
                'title': 'The author'},
        'collection': {'href': url_for('authors'),
                        'title': 'Authors list'}
    }

def test_hyperlinks_field_deserialization(ma):
    field = ma.Hyperlinks({
        'href': ma.URLFor('author', id='<id>')
    })
    # noop
    assert field.deserialize('/author') == '/author'
    assert field.deserialize(None) is None

def test_absolute_url(ma, mockauthor):
    field = ma.AbsoluteURLFor('authors')
    result = field.serialize('abs_url', mockauthor)
    assert result == url_for('authors', _external=True)

def test_absolute_url_deserialization(ma):
    field = ma.AbsoluteURLFor('authors')
    assert field.deserialize('foo') == 'foo'
    assert field.deserialize(None) is None

def test_deferred_initialization():
    app = Flask(__name__)
    m = Marshmallow()
    m.init_app(app)

    assert 'flask-marshmallow' in app.extensions

def test_aliases(ma):
    from flask_marshmallow.fields import UrlFor, AbsoluteUrlFor, URLFor, AbsoluteURLFor
    assert UrlFor is URLFor
    assert AbsoluteUrlFor is AbsoluteURLFor

class AuthorSchema(mar.Schema):
    class Meta:
        fields = ('id', 'name', 'absolute_url', 'links')

    absolute_url = mar.AbsoluteURLFor('author', id='<id>')

    links = mar.Hyperlinks({
        'self': mar.URLFor('author', id='<id>'),
        'collection': mar.URLFor('authors')
    })

class BookSchema(mar.Schema):
    class Meta:
        fields = ('id', 'title', 'author', 'links')

    author = mar.Nested(AuthorSchema)

    links = mar.Hyperlinks({
        'self': mar.URLFor('book', id='<id>'),
        'collection': mar.URLFor('books'),
    })

def test_schema(app, mockauthor):
    s = AuthorSchema()
    result = s.dump(mockauthor)
    assert result.data['id'] == mockauthor.id
    assert result.data['name'] == mockauthor.name
    assert result.data['absolute_url'] == url_for('author',
        id=mockauthor.id, _external=True)
    links = result.data['links']
    assert links['self'] == url_for('author', id=mockauthor.id)
    assert links['collection'] == url_for('authors')

def test_jsonify(app, mockauthor):
    s = AuthorSchema(mockauthor)
    resp = s.jsonify()
    assert isinstance(resp, BaseResponse)
    assert resp.content_type == 'application/json'

def test_links_within_nested_object(app, mockbook):
    s = BookSchema()
    result = s.dump(mockbook)
    assert result.data['title'] == mockbook.title
    author = result.data['author']
    assert author['links']['self'] == url_for('author', id=mockbook.author.id)
    assert author['links']['collection'] == url_for('authors')

class ConfigTestCase:

    def set_config(self, app):
        pass

    def setup_method(self, method):
        self.app = Flask(__name__)
        self.set_config(self.app)

        ma = Marshmallow()
        ma.init_app(self.app)

        class _Schema(ma.Schema):
            meaning = ma.Integer()

        self.Schema = _Schema

        self.obj = mock.Mock()
        self.obj.meaning = 42
