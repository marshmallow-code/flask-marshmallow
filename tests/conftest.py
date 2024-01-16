"""Pytest fixtures for the test suite."""
import pytest
from flask import Flask

from flask_marshmallow import Marshmallow

_app = Flask(__name__)
_app.testing = True


class Bunch(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self


# Models


class Author(Bunch):
    pass


class Book(Bunch):
    pass


@pytest.fixture
def mockauthor():
    author = Author(id=123, name="Fred Douglass")
    return author


@pytest.fixture
def mockauthorlist():
    a1 = Author(id=1, name="Alice")
    a2 = Author(id=2, name="Bob")
    a3 = Author(id=3, name="Carol")
    return [a1, a2, a3]


@pytest.fixture
def mockbook(mockauthor):
    book = Book(id=42, author=mockauthor, title="Legend of Bagger Vance")
    return book


@_app.route("/author/<int:id>")
def author(id):
    return "Steven Pressfield"


@_app.route("/authors/")
def authors():
    return "Steven Pressfield, Chuck Paluhniuk"


@_app.route("/books/")
def books():
    return "Legend of Bagger Vance, Fight Club"


@_app.route("/books/<id>")
def book(id):
    return "Legend of Bagger Vance"


@pytest.fixture(scope="function")
def app():
    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture(scope="function")
def ma(app):
    return Marshmallow(app)


@pytest.fixture
def schemas(ma):
    class AuthorSchema(ma.Schema):
        class Meta:
            fields = ("id", "name", "absolute_url", "links")

        absolute_url = ma.AbsoluteURLFor("author", values={"id": "<id>"})

        links = ma.Hyperlinks(
            {
                "self": ma.URLFor("author", values={"id": "<id>"}),
                "collection": ma.URLFor("authors"),
            }
        )

    class BookSchema(ma.Schema):
        class Meta:
            fields = ("id", "title", "author", "links")

        author = ma.Nested(AuthorSchema)

        links = ma.Hyperlinks(
            {
                "self": ma.URLFor("book", values={"id": "<id>"}),
                "collection": ma.URLFor("books"),
            }
        )

    # So we can access schemas.AuthorSchema, etc.
    return Bunch(**locals())
