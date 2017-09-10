*********************************************************
Flask-Marshmallow: Flask + marshmallow for beautiful APIs
*********************************************************

:ref:`changelog <changelog>` //
`github <http://github.com/marshmallow-code/flask-marshmallow>`_ //
`pypi <http://pypi.python.org/pypi/flask-marshmallow>`_ //
`issues <http://github.com/marshmallow-code/flask-marshmallow/issues>`_


Flask + marshmallow for beautiful APIs
======================================

Flask-Marshmallow is a thin integration layer for `Flask`_ (a Python web framework) and `marshmallow`_ (an object serialization/deserialization library) that adds additional features to marshmallow, including URL and Hyperlinks fields for HATEOAS-ready APIs. It also (optionally) integrates with `Flask-SQLAlchemy <http://flask-sqlalchemy.pocoo.org/>`_.

Get it now
----------
::

    pip install flask-marshmallow


Create your app.

.. code-block:: python

    from flask import Flask, jsonify
    from flask_marshmallow import Marshmallow

    app = Flask(__name__)
    ma = Marshmallow(app)

Write your models.

.. code-block:: python

    from your_orm import Model, Column, Integer, String, DateTime

    class User(Model):
        email = Column(String)
        password = Column(String)
        date_created = Column(DateTime, auto_now_add=True)


Define your output format with marshmallow.

.. code-block:: python


    class UserSchema(ma.Schema):
        class Meta:
            # Fields to expose
            fields = ('email', 'date_created', '_links')
        # Smart hyperlinking
        _links = ma.Hyperlinks({
            'self': ma.URLFor('user_detail', id='<id>'),
            'collection': ma.URLFor('users')
        })

    user_schema = UserSchema()
    users_schema = UserSchema(many=True)


Output the data in your views.

.. code-block:: python

    @app.route('/api/users/')
    def users():
        all_users = User.all()
        result = users_schema.dump(all_users)
        return jsonify(result.data)
        # OR
        # return user_schema.jsonify(all_users)

    @app.route('/api/users/<id>')
    def user_detail(id):
        user = User.get(id)
        return user_schema.jsonify(user)
    # {
    #     "email": "fred@queen.com",
    #     "date_created": "Fri, 25 Apr 2014 06:02:56 -0000",
    #     "_links": {
    #         "self": "/api/users/42",
    #         "collection": "/api/users/"
    #     }
    # }



Optional Flask-SQLAlchemy Integration
-------------------------------------

Flask-Marshmallow includes useful extras for integrating with `Flask-SQLAlchemy <http://flask-sqlalchemy.pocoo.org/>`_ and `marshmallow-sqlalchemy <https://marshmallow-sqlalchemy.readthedocs.io>`_.

To enable SQLAlchemy integration, make sure that both Flask-SQLAlchemy and marshmallow-sqlalchemy are installed.  ::

    pip install -U flask-sqlalchemy marshmallow-sqlalchemy

Next, initialize the `~flask_sqlalchemy.SQLAlchemy` and `~flask_marshmallow.Marshmallow` extensions, in that order.

.. code-block:: python

    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    from flask_marshmallow import Marshmallow

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'

    # Order matters: Initialize SQLAlchemy before Marshmallow
    db = SQLAlchemy(app)
    ma = Marshmallow(app)

.. admonition:: Note on initialization order

    Flask-SQLAlchemy **must** be initialized before Flask-Marshmallow.


Declare your models like normal.


.. code-block:: python

    class Author(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(255))

    class Book(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(255))
        author_id = db.Column(db.Integer, db.ForeignKey('author.id'))
        author = db.relationship('Author', backref='books')


Generate marshmallow `Schemas <marshmallow.Schema>` from your models using `~flask_marshmallow.sqla.ModelSchema`.

.. code-block:: python

    class AuthorSchema(ma.ModelSchema):
        class Meta:
            model = Author

    class BookSchema(ma.ModelSchema):
        class Meta:
            model = Book

You can now use your schema to dump and load your ORM objects.


.. code-block:: python

    >>> db.create_all()
    >>> author_schema = AuthorSchema()
    >>> book_schema = BookSchema()
    >>> author = Author(name='Chuck Paluhniuk')
    >>> book = Book(title='Fight Club', author=author)
    >>> db.session.add(author)
    >>> db.session.add(book)
    >>> db.session.commit()
    >>> author_schema.dump(author).data
    {'id': 1, 'name': 'Chuck Paluhniuk', 'books': [1]}


`~flask_marshmallow.sqla.ModelSchema` is nearly identical in API to `marshmallow_sqlalchemy.ModelSchema` with the following exceptions:

- By default, `~flask_marshmallow.sqla.ModelSchema` uses the scoped session created by Flask-SQLAlchemy.
- `~flask_marshmallow.sqla.ModelSchema` subclasses `flask_marshmallow.Schema`, so it includes the `~flask_marshmallow.Schema.jsonify` method.
Note: By default, Flask's `jsonify` method sorts the list of keys and returns consistent results to ensure that external HTTP caches aren't trashed. As a side effect, this will override `ordered=True <https://marshmallow.readthedocs.io/en/latest/quickstart.html#ordering-output>`_ in the ModelSchema's `class Meta` (if you set it). To disable this, set `JSON_SORT_KEYS=False` in your Flask app config. In production it's recommended to let `jsonify` sort the keys and not set `ordered=True` in your `~flask_marshmallow.sqla.ModelSchema` in order to minimize generation time and maximize cachability of the results.

You can also use `ma.HyperlinkRelated <flask_marshmallow.sqla.HyperlinkRelated>` fields if you want relationships to be represented by hyperlinks rather than primary keys.


.. code-block:: python

    class BookSchema(ma.ModelSchema):
        class Meta:
            model = Book
        author = ma.HyperlinkRelated('author_detail')

.. code-block:: python

    >>> with app.test_request_context():
    ...     print(book_schema.dump(book).data)
    {'id': 1, 'title': 'Fight Club', 'author': '/authors/1'}

The first argument to the `~flask_marshmallow.sqla.HyperlinkRelated` constructor is the name of the view used to generate the URL, just as you would pass it to the `~flask.url_for` function. If your models and views use the ``id`` attribute
as a primary key, you're done; otherwise, you must specify the name of the
attribute used as the primary key.

To represent a one-to-many relationship, wrap the `~flask_marshmallow.sqla.HyperlinkRelated` instance in a `marshmallow.fields.List` field, like this:

.. code-block:: python

    class AuthorSchema(ma.ModelSchema):
        class Meta:
            model = Author
        books = ma.List(ma.HyperlinkRelated('book_detail'))

.. code-block:: python

    >>> with app.test_request_context():
    ...     print(author_schema.dump(author).data)
    {'id': 1, 'name': 'Chuck Paluhniuk', 'books': ['/books/1']}


API
===

.. automodule:: flask_marshmallow
    :members:

.. automodule:: flask_marshmallow.fields
    :members:

.. automodule:: flask_marshmallow.sqla
    :members:


Useful Links
============

- `Flask docs`_
- `marshmallow docs`_

.. _marshmallow docs: http://marshmallow.readthedocs.io

.. _Flask docs: http://flask.pocoo.org/docs/

Project Info
============

.. toctree::
   :maxdepth: 1

   license
   changelog


.. _marshmallow: http://marshmallow.readthedocs.io

 .. _Flask: http://flask.pocoo.org
