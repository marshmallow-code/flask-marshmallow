# -*- coding: utf-8 -*-
import mock
import pytest

from flask import Flask, url_for
from werkzeug.routing import BuildError
from werkzeug.wrappers import BaseResponse

from flask_marshmallow import Serializer, fields, pprint
from flask_marshmallow.fields import Hyperlinks, URL, _tpl, AbsoluteURL

@pytest.yield_fixture(scope='function')
def app():
    _app = Flask('Testing app')

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

    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()


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

def test_url_field(app, mockauthor):
    field = URL('author', id='<id>')
    result = field.output('url', mockauthor)
    assert result == url_for('author', id=mockauthor.id)

def test_url_field_with_invalid_attribute(app, mockauthor):
    field = URL('author', id='<not-an-attr>')
    with pytest.raises(AttributeError) as excinfo:
        field.output('url', mockauthor)
    expected_msg = '{0!r} is not a valid attribute of {1!r}'.format(
        'not-an-attr', mockauthor)
    assert expected_msg in str(excinfo)

def test_invalid_endpoint_raises_build_error(app, mockauthor):
    field = URL('badendpoint')
    with pytest.raises(BuildError):
        field.output('url', mockauthor)

def test_hyperlinks_field(app, mockauthor):
    field = Hyperlinks({
        'self': URL('author', id='<id>'),
        'collection': URL('authors')
    })

    result = field.output('_links', mockauthor)
    assert result == {
        'self': url_for('author', id=mockauthor.id),
        'collection': url_for('authors')
    }

def test_hyperlinks_field_recurses(app, mockauthor):
    field = Hyperlinks({
        'self': {
            'href': URL('author', id='<id>'),
            'title': 'The author'
        },
        'collection': {
            'href': URL('authors'),
            'title': 'Authors list'
        }
    })
    result = field.output('_links', mockauthor)

    assert result == {
        'self': {'href': url_for('author', id=mockauthor.id),
                'title': 'The author'},
        'collection': {'href': url_for('authors'),
                        'title': 'Authors list'}
    }

def test_absolute_url(app, mockauthor):
    field = AbsoluteURL('authors')
    result = field.output('abs_url', mockauthor)
    assert result == url_for('authors', _external=True)

def test_aliases():
    from flask_marshmallow.fields import Url, AbsoluteUrl
    assert Url == URL
    assert AbsoluteUrl == AbsoluteURL

class AuthorMarshal(Serializer):
    class Meta:
        fields = ('id', 'name', 'absolute_url', 'links')

    absolute_url = AbsoluteURL('author', id='<id>')

    links = fields.Hyperlinks({
        'self': fields.URL('author', id='<id>'),
        'collection': fields.URL('authors')
    })

class BookMarshal(Serializer):
    class Meta:
        fields = ('id', 'title', 'author', 'links')

    author = fields.Nested(AuthorMarshal)

    links = fields.Hyperlinks({
        'self': fields.URL('book', id='<id>'),
        'collection': fields.URL('books'),
    })

def test_serializer(app, mockauthor):
    s = AuthorMarshal(mockauthor)
    assert s.data['id'] == mockauthor.id
    assert s.data['name'] == mockauthor.name
    assert s.data['absolute_url'] == url_for('author',
        id=mockauthor.id, _external=True)
    links = s.data['links']
    assert links['self'] == url_for('author', id=mockauthor.id)
    assert links['collection'] == url_for('authors')

def test_jsonify(app, mockauthor):
    s = AuthorMarshal(mockauthor)
    resp = s.jsonify()
    assert isinstance(resp, BaseResponse)
    assert resp.content_type == 'application/json'

def test_links_within_nested_object(app, mockbook):
    s = BookMarshal(mockbook)
    assert s.data['title'] == mockbook.title
    author = s.data['author']
    assert author['links']['self'] == url_for('author', id=mockbook.author.id)
    assert author['links']['collection'] == url_for('authors')
