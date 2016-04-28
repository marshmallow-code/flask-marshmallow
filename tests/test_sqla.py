# -*- coding: utf-8 -*-
from flask import Flask, url_for
from flask_marshmallow import Marshmallow
from flask_marshmallow.sqla import HyperlinkRelated
from flask_sqlalchemy import SQLAlchemy
from werkzeug.wrappers import BaseResponse
import marshmallow
import pytest

from tests.conftest import Bunch

MARSHMALLOW_2 = int(marshmallow.__version__.split('.')[0]) >= 2

@pytest.mark.skipif(not MARSHMALLOW_2, reason='marshmallow-sqlalchemy '
                    'not supported in marshmallow<2.0')
class TestSQLAlchemy:

    @pytest.yield_fixture()
    def extapp(self):
        app_ = Flask('extapp')
        app_.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        SQLAlchemy(app_)
        Marshmallow(app_)

        @app_.route('/author/<int:id>')
        def author(id):
            return '...view for author {0}...'.format(id)

        @app_.route('/book/<int:id>')
        def book(id):
            return '...view for book {0}...'.format(id)

        ctx = app_.test_request_context()
        ctx.push()

        yield app_

        ctx.pop()

    @pytest.fixture()
    def db(self, extapp):
        return extapp.extensions['sqlalchemy'].db

    @pytest.fixture()
    def extma(self, extapp):
        return extapp.extensions['flask-marshmallow']

    @pytest.yield_fixture()
    def models(self, db):
        class AuthorModel(db.Model):
            __tablename__ = 'author'
            id = db.Column(db.Integer, primary_key=True)
            name = db.Column(db.String(255))

            @property
            def url(self):
                return url_for('author', id=self.id)

            @property
            def absolute_url(self):
                return url_for('author', id=self.id, _external=True)

        class BookModel(db.Model):
            __tablename__ = 'book'
            id = db.Column(db.Integer, primary_key=True)
            title = db.Column(db.String(255))
            author_id = db.Column(db.Integer, db.ForeignKey('author.id'))
            author = db.relationship('AuthorModel', backref='books')

            @property
            def url(self):
                return url_for('book', id=self.id)

            @property
            def absolute_url(self):
                return url_for('book', id=self.id, _external=True)

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

        author = models.Author(name='Chuck Paluhniuk')
        db.session.add(author)
        db.session.commit()

        author = models.Author(name='Chuck Paluhniuk')
        book = models.Book(title='Fight Club', author=author)
        db.session.add(author)
        db.session.add(book)
        db.session.commit()

        author_result = author_schema.dump(author)
        assert 'id' in author_result.data
        assert 'name' in author_result.data
        assert author_result.data['name'] == 'Chuck Paluhniuk'
        assert author_result.data['books'][0] == book.id

        book_result = book_schema.dump(book)
        assert 'id' in book_result.data
        assert book_result.data['author'] == author.id

        resp = author_schema.jsonify(author)
        assert isinstance(resp, BaseResponse)

    def test_hyperlink_related_field(self, extma, models, db, extapp):
        class BookSchema(extma.ModelSchema):
            class Meta:
                model = models.Book
            author = extma.HyperlinkRelated('author')

        book_schema = BookSchema()

        author = models.Author(name='Chuck Paluhniuk')
        book = models.Book(title='Fight Club', author=author)
        db.session.add(author)
        db.session.add(book)
        db.session.flush()

        book_result = book_schema.dump(book)
        assert book_result.data['author'] == author.url

        deserialized = book_schema.load(book_result.data)
        assert deserialized.data.author == author

    def test_hyperlink_related_field_errors(self, extma, models, db, extapp):
        class BookSchema(extma.ModelSchema):
            class Meta:
                model = models.Book
            author = HyperlinkRelated('author')

        book_schema = BookSchema()

        author = models.Author(name='Chuck Paluhniuk')
        book = models.Book(title='Fight Club', author=author)
        db.session.add(author)
        db.session.add(book)
        db.session.flush()

        # Deserialization fails on bad endpoint
        book_result = book_schema.dump(book)
        book_result.data['author'] = book.url
        deserialized = book_schema.load(book_result.data)
        assert 'expected "author"' in deserialized.errors['author'][0]

        # Deserialization fails on bad URL key
        book_result = book_schema.dump(book)
        book_schema.fields['author'].url_key = 'pk'
        deserialized = book_schema.load(book_result.data)
        assert 'URL pattern "pk" not found' in deserialized.errors['author'][0]

    def test_hyperlink_related_field_external(self, extma, models, db, extapp):
        class BookSchema(extma.ModelSchema):
            class Meta:
                model = models.Book
            author = HyperlinkRelated('author', external=True)

        book_schema = BookSchema()

        author = models.Author(name='Chuck Paluhniuk')
        book = models.Book(title='Fight Club', author=author)
        db.session.add(author)
        db.session.add(book)
        db.session.flush()

        book_result = book_schema.dump(book)
        assert book_result.data['author'] == author.absolute_url

        deserialized = book_schema.load(book_result.data)
        assert deserialized.data.author == author

    def test_hyperlink_related_field_list(self, extma, models, db, extapp):
        class AuthorSchema(extma.ModelSchema):
            class Meta:
                model = models.Author
            books = extma.List(HyperlinkRelated('book'))

        author_schema = AuthorSchema()

        author = models.Author(name='Chuck Paluhniuk')
        book = models.Book(title='Fight Club', author=author)
        db.session.add(author)
        db.session.add(book)
        db.session.flush()

        author_result = author_schema.dump(author)
        assert author_result.data['books'][0] == book.url

        deserialized = author_schema.load(author_result.data)
        assert deserialized.data.books[0] == book
