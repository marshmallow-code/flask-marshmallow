import pytest
from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
from marshmallow import ValidationError
from werkzeug.wrappers import Response

from flask_marshmallow import Marshmallow
from flask_marshmallow.sqla import HyperlinkRelated
from tests.conftest import Bunch

try:
    from marshmallow_sqlalchemy import SQLAlchemySchema  # noqa: F401
except ImportError:
    has_sqlalchemyschema = False
else:
    has_sqlalchemyschema = True


requires_sqlalchemyschema = pytest.mark.skipif(
    not has_sqlalchemyschema, reason="SQLAlchemySchema not available"
)


class TestSQLAlchemy:
    @pytest.fixture
    def extapp(self):
        app_ = Flask("extapp")
        app_.testing = True
        app_.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app_.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        SQLAlchemy(app_)
        Marshmallow(app_)

        @app_.route("/author/<int:id>")
        def author(id):
            return f"...view for author {id}..."

        @app_.route("/book/<int:id>")
        def book(id):
            return f"...view for book {id}..."

        ctx = app_.test_request_context()
        ctx.push()

        yield app_

        ctx.pop()

    @pytest.fixture
    def db(self, extapp):
        return extapp.extensions["sqlalchemy"]

    @pytest.fixture
    def extma(self, extapp):
        return extapp.extensions["flask-marshmallow"]

    @pytest.fixture
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

    def test_can_initialize_extensions(self, extapp):
        assert "flask-marshmallow" in extapp.extensions
        assert "sqlalchemy" in extapp.extensions

    @requires_sqlalchemyschema
    def test_can_declare_sqla_schemas(self, extma, models, db):
        class AuthorSchema(extma.SQLAlchemySchema):
            class Meta:
                model = models.Author

            id = extma.auto_field()
            name = extma.auto_field()

        class BookSchema(extma.SQLAlchemySchema):
            class Meta:
                model = models.Book

            id = extma.auto_field()
            title = extma.auto_field()
            author_id = extma.auto_field()

        author_schema = AuthorSchema()
        book_schema = BookSchema()

        author = models.Author(name="Chuck Paluhniuk")
        book = models.Book(title="Fight Club", author=author)

        author_result = author_schema.dump(author)

        assert "id" in author_result
        assert "name" in author_result
        assert author_result["id"] == author.id
        assert author_result["name"] == "Chuck Paluhniuk"
        book_result = book_schema.dump(book)

        assert "id" in book_result
        assert "title" in book_result
        assert book_result["id"] == book.id
        assert book_result["title"] == book.title
        assert book_result["author_id"] == book.author_id

        resp = author_schema.jsonify(author)
        assert isinstance(resp, Response)

    @requires_sqlalchemyschema
    def test_can_declare_sqla_auto_schemas(self, extma, models, db):
        class AuthorSchema(extma.SQLAlchemyAutoSchema):
            class Meta:
                model = models.Author

        class BookSchema(extma.SQLAlchemyAutoSchema):
            class Meta:
                model = models.Book
                include_fk = True

            id = extma.auto_field()
            title = extma.auto_field()
            author_id = extma.auto_field()

        author_schema = AuthorSchema()
        book_schema = BookSchema()

        author = models.Author(name="Chuck Paluhniuk")
        book = models.Book(title="Fight Club", author=author)

        author_result = author_schema.dump(author)

        assert "id" in author_result
        assert "name" in author_result
        assert author_result["id"] == author.id
        assert author_result["name"] == "Chuck Paluhniuk"
        book_result = book_schema.dump(book)

        assert "id" in book_result
        assert "title" in book_result
        assert book_result["id"] == book.id
        assert book_result["title"] == book.title
        assert book_result["author_id"] == book.author_id

        resp = author_schema.jsonify(author)
        assert isinstance(resp, Response)

    # FIXME: temporarily filter out this warning
    # this is triggered by marshmallow-sqlalchemy on sqlalchemy v1.4.x
    # on the current version it should be fixed
    # in an upcoming marshmallow-sqlalchemy release
    @requires_sqlalchemyschema
    def test_hyperlink_related_field(self, extma, models, db, extapp):
        class BookSchema(extma.SQLAlchemySchema):
            class Meta:
                model = models.Book

            author = extma.HyperlinkRelated("author")

        book_schema = BookSchema()

        author = models.Author(name="Chuck Paluhniuk")
        book = models.Book(title="Fight Club", author=author)
        db.session.add(author)
        db.session.add(book)
        db.session.flush()

        book_result = book_schema.dump(book)

        assert book_result["author"] == author.url

        deserialized = book_schema.load(book_result)
        assert deserialized["author"] == author

    @requires_sqlalchemyschema
    def test_hyperlink_related_field_serializes_none(self, extma, models):
        class BookSchema(extma.SQLAlchemySchema):
            class Meta:
                model = models.Book

            author = extma.HyperlinkRelated("author")

        book_schema = BookSchema()
        book = models.Book(title="Fight Club", author=None)
        book_result = book_schema.dump(book)
        assert book_result["author"] is None

    @requires_sqlalchemyschema
    def test_hyperlink_related_field_errors(self, extma, models, db, extapp):
        class BookSchema(extma.SQLAlchemySchema):
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
        book_result = book_schema.dump(book)
        book_result["author"] = book.url
        with pytest.raises(ValidationError) as excinfo:
            book_schema.load(book_result)
        errors = excinfo.value.messages
        assert 'expected "author"' in errors["author"][0]

        # Deserialization fails on bad URL key
        book_result = book_schema.dump(book)
        book_schema.fields["author"].url_key = "pk"
        with pytest.raises(ValidationError) as excinfo:
            book_schema.load(book_result)
        errors = excinfo.value.messages
        assert 'URL pattern "pk" not found' in errors["author"][0]

    @requires_sqlalchemyschema
    def test_hyperlink_related_field_external(self, extma, models, db, extapp):
        class BookSchema(extma.SQLAlchemySchema):
            class Meta:
                model = models.Book

            author = HyperlinkRelated("author", external=True)

        book_schema = BookSchema()

        author = models.Author(name="Chuck Paluhniuk")
        book = models.Book(title="Fight Club", author=author)
        db.session.add(author)
        db.session.add(book)
        db.session.flush()

        book_result = book_schema.dump(book)

        assert book_result["author"] == author.absolute_url

        deserialized = book_schema.load(book_result)
        assert deserialized["author"] == author

    @requires_sqlalchemyschema
    def test_hyperlink_related_field_list(self, extma, models, db, extapp):
        class AuthorSchema(extma.SQLAlchemySchema):
            class Meta:
                model = models.Author

            books = extma.List(HyperlinkRelated("book"))

        author_schema = AuthorSchema()

        author = models.Author(name="Chuck Paluhniuk")
        book = models.Book(title="Fight Club", author=author)
        db.session.add(author)
        db.session.add(book)
        db.session.flush()

        author_result = author_schema.dump(author)
        assert author_result["books"][0] == book.url

        deserialized = author_schema.load(author_result)
        assert deserialized["books"][0] == book
