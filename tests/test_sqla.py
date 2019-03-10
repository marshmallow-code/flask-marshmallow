# -*- coding: utf-8 -*-
import pytest
from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.wrappers import BaseResponse

from flask_marshmallow import Marshmallow
from flask_marshmallow.sqla import HyperlinkRelated
from tests.conftest import Bunch
from tests.utils import get_dump_data, get_load_data


class TestSQLAlchemy:
    @pytest.yield_fixture()
    def extapp(self):
        app_ = Flask("extapp")
        app_.testing = True
        app_.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app_.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        SQLAlchemy(app_)
        Marshmallow(app_)

        @app_.route("/author/<int:id>")
        def author(id):
            return "...view for author {}...".format(id)

        @app_.route("/book/<int:id>")
        def book(id):
            return "...view for book {}...".format(id)

        ctx = app_.test_request_context()
        ctx.push()

        yield app_

        ctx.pop()

    @pytest.fixture()
    def db(self, extapp):
        return extapp.extensions["sqlalchemy"].db

    @pytest.fixture()
    def extma(self, extapp):
        return extapp.extensions["flask-marshmallow"]

    @pytest.yield_fixture()
    def models(self, db):
        class AuthorModel(db.Model):
            __tablename__ = "author"
            id = db.Column(db.Integer, primary_key=True)
            name = db.Column(db.String(255))

            @property
            def url(self):
                return url_for("author", id=self.id)

            @property
            def absolute_url(self):
                return url_for("author", id=self.id, _external=True)

        class BookModel(db.Model):
            __tablename__ = "book"
            id = db.Column(db.Integer, primary_key=True)
            title = db.Column(db.String(255))
            author_id = db.Column(db.Integer, db.ForeignKey("author.id"))
            author = db.relationship("AuthorModel", backref="books")

            @property
            def url(self):
                return url_for("book", id=self.id)

            @property
            def absolute_url(self):
                return url_for("book", id=self.id, _external=True)

        db.create_all()
        yield Bunch(Author=AuthorModel, Book=BookModel)
        db.drop_all()

    def test_can_declare_model_schemas(self, extma, models, db):
        class AuthorSchema(extma.ModelSchema):
            class Meta:
                model = models.Author

        class BookSchema(extma.ModelSchema):
            class Meta:
                model = models.Book

        author_schema = AuthorSchema()
        book_schema = BookSchema()

        author = models.Author(name="Chuck Paluhniuk")
        book = models.Book(title="Fight Club", author=author)

        author_result = get_dump_data(author_schema, author)

        assert "id" in author_result
        assert "name" in author_result
        assert author_result["name"] == "Chuck Paluhniuk"
        assert author_result["books"][0] == book.id
        book_result = get_dump_data(book_schema, book)

        assert "id" in book_result
        assert book_result["author"] == author.id

        resp = author_schema.jsonify(author)
        assert isinstance(resp, BaseResponse)

    def test_can_declare_table_schemas(self, extma, models, db):
        class AuthorSchema(extma.TableSchema):
            class Meta:
                table = models.Author.__table__

        class BookSchema(extma.TableSchema):
            class Meta:
                table = models.Book.__table__

        author_schema = AuthorSchema()
        book_schema = BookSchema()

        author = models.Author(name="Chuck Paluhniuk")
        book = models.Book(title="Fight Club", author=author)

        author_result = get_dump_data(author_schema, author)

        assert "id" in author_result
        assert "name" in author_result
        assert author_result["id"] == author.id
        assert author_result["name"] == "Chuck Paluhniuk"
        book_result = get_dump_data(book_schema, book)

        assert "id" in book_result
        assert "title" in book_result
        assert book_result["id"] == book.id
        assert book_result["title"] == book.title

        resp = author_schema.jsonify(author)
        assert isinstance(resp, BaseResponse)

    def test_hyperlink_related_field(self, extma, models, db, extapp):
        class BookSchema(extma.ModelSchema):
            class Meta:
                model = models.Book

            author = extma.HyperlinkRelated("author")

        book_schema = BookSchema()

        author = models.Author(name="Chuck Paluhniuk")
        book = models.Book(title="Fight Club", author=author)
        db.session.add(author)
        db.session.add(book)
        db.session.flush()

        book_result = get_dump_data(book_schema, book)

        assert book_result["author"] == author.url

        deserialized, errors = get_load_data(book_schema, book_result)
        assert deserialized.author == author

    def test_hyperlink_related_field_serializes_none(self, extma, models):
        class BookSchema(extma.ModelSchema):
            class Meta:
                model = models.Book

            author = extma.HyperlinkRelated("author")

        book_schema = BookSchema()
        book = models.Book(title="Fight Club", author=None)
        book_result = get_dump_data(book_schema, book)
        assert book_result["author"] is None

    def test_hyperlink_related_field_errors(self, extma, models, db, extapp):
        class BookSchema(extma.ModelSchema):
            class Meta:
                model = models.Book

            author = HyperlinkRelated("author")

        book_schema = BookSchema()

        author = models.Author(name="Chuck Paluhniuk")
        book = models.Book(title="Fight Club", author=author)
        db.session.add(author)
        db.session.add(book)
        db.session.flush()

        # Deserialization fails on bad endpoint
        book_result = get_dump_data(book_schema, book)
        book_result["author"] = book.url
        deserialized, errors = get_load_data(book_schema, book_result)
        assert 'expected "author"' in errors["author"][0]

        # Deserialization fails on bad URL key
        book_result = get_dump_data(book_schema, book)
        book_schema.fields["author"].url_key = "pk"
        deserialized, errors = get_load_data(book_schema, book_result)
        assert 'URL pattern "pk" not found' in errors["author"][0]

    def test_hyperlink_related_field_external(self, extma, models, db, extapp):
        class BookSchema(extma.ModelSchema):
            class Meta:
                model = models.Book

            author = HyperlinkRelated("author", external=True)

        book_schema = BookSchema()

        author = models.Author(name="Chuck Paluhniuk")
        book = models.Book(title="Fight Club", author=author)
        db.session.add(author)
        db.session.add(book)
        db.session.flush()

        book_result = get_dump_data(book_schema, book)

        assert book_result["author"] == author.absolute_url

        deserialized, errors = get_load_data(book_schema, book_result)
        assert deserialized.author == author

    def test_hyperlink_related_field_list(self, extma, models, db, extapp):
        class AuthorSchema(extma.ModelSchema):
            class Meta:
                model = models.Author

            books = extma.List(HyperlinkRelated("book"))

        author_schema = AuthorSchema()

        author = models.Author(name="Chuck Paluhniuk")
        book = models.Book(title="Fight Club", author=author)
        db.session.add(author)
        db.session.add(book)
        db.session.flush()

        author_result = get_dump_data(author_schema, author)
        assert author_result["books"][0] == book.url

        deserialized, errors = get_load_data(author_schema, author_result)
        assert deserialized.books[0] == book
