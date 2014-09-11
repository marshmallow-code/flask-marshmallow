# -*- coding: utf-8 -*-
import mock
import pytest

from flask import Flask, url_for
from werkzeug.routing import BuildError
from werkzeug.wrappers import BaseResponse

from flask.ext.marshmallow import Marshmallow
from flask.ext.marshmallow.fields import _tpl
from flask.ext.marshmallow import exceptions

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
    field = ma.URL('author', id='<id>')
    result = field.serialize('url', mockauthor)
    assert result == url_for('author', id=mockauthor.id)

def test_url_field_with_invalid_attribute(ma, mockauthor):
    field = ma.URL('author', id='<not-an-attr>')
    with pytest.raises(AttributeError) as excinfo:
        field.serialize('url', mockauthor)
    expected_msg = '{0!r} is not a valid attribute of {1!r}'.format(
        'not-an-attr', mockauthor)
    assert expected_msg in str(excinfo)

def test_invalid_endpoint_raises_build_error(ma, mockauthor):
    field = ma.URL('badendpoint')
    with pytest.raises(BuildError):
        field.serialize('url', mockauthor)

def test_hyperlinks_field(ma, mockauthor):
    field = ma.Hyperlinks({
        'self': ma.URL('author', id='<id>'),
        'collection': ma.URL('authors')
    })

    result = field.serialize('_links', mockauthor)
    assert result == {
        'self': url_for('author', id=mockauthor.id),
        'collection': url_for('authors')
    }

def test_hyperlinks_field_recurses(ma, mockauthor):
    field = ma.Hyperlinks({
        'self': {
            'href': ma.URL('author', id='<id>'),
            'title': 'The author'
        },
        'collection': {
            'href': ma.URL('authors'),
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

def test_absolute_url(ma, mockauthor):
    field = ma.AbsoluteURL('authors')
    result = field.serialize('abs_url', mockauthor)
    assert result == url_for('authors', _external=True)

def test_deferred_initialization():
    app = Flask(__name__)
    m = Marshmallow()
    m.init_app(app)

    assert 'flask-marshmallow' in app.extensions

def test_aliases(ma):
    from flask_marshmallow.fields import Url, AbsoluteUrl, URL, AbsoluteURL
    assert Url is URL
    assert AbsoluteUrl is AbsoluteURL

class AuthorSchema(mar.Schema):
    class Meta:
        fields = ('id', 'name', 'absolute_url', 'links')

    absolute_url = mar.AbsoluteURL('author', id='<id>')

    links = mar.Hyperlinks({
        'self': mar.URL('author', id='<id>'),
        'collection': mar.URL('authors')
    })

class BookSchema(mar.Schema):
    class Meta:
        fields = ('id', 'title', 'author', 'links')

    author = mar.Nested(AuthorSchema)

    links = mar.Hyperlinks({
        'self': mar.URL('book', id='<id>'),
        'collection': mar.URL('books'),
    })

def test_serializer(app, mockauthor):
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


class TestStrictConfig(ConfigTestCase):

    def set_config(self, app):
        app.config['MARSHMALLOW_STRICT'] = True

    def test_strict_mode_default(self):
        with self.app.test_request_context():
            serialized = self.Schema(self.obj)
            assert serialized.strict is True
            with pytest.raises(exceptions.MarshallingError):
                badobj = mock.Mock()
                badobj.meaning = 'bad'
                self.Schema(badobj)

    def test_strict_mode_override(self):
        ma = Marshmallow(self.app)

        class MySchema(ma.Schema):
            meaning = ma.Integer()
            # override strict mode
            class Meta:
                strict = False

        with self.app.test_request_context():
            serialized = MySchema(self.obj)
            assert serialized.strict is False

class TestDateformatConfig(ConfigTestCase):

    def set_config(self, app):
        self.app.config['MARSHMALLOW_DATEFORMAT'] = 'iso'

    def test_dateformat_default(self):
        with self.app.test_request_context():
            serialized = self.Schema()
            assert serialized.opts.dateformat == 'iso'

    def test_dateformat_override(self):
        ma = Marshmallow(self.app)
        class MySchema(self.Schema):
            class Meta:
                dateformat = '%d'
        with self.app.test_request_context():
            s = MySchema(self.obj)
            assert s.opts.dateformat == '%d'
