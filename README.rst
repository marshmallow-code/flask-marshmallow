*****************
Flask-Marshmallow
*****************

|pypi-package| |build-status| |coverage-status| |docs|

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
            'self': ma.URLFor('author_detail', id='<id>'),
            'collection': ma.URLFor('authors')
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
    #         "self": "/api/authors/42",
    #         "collection": "/api/authors/"
    #     }
    # }


http://flask-marshmallow.readthedocs.io/
========================================

Learn More
==========

To learn more about marshmallow, check out its `docs <http://marshmallow.readthedocs.io/en/latest/>`_.



Project Links
=============

- Docs: http://flask-marshmallow.rtfd.org/
- Changelog: http://flask-marshmallow.readthedocs.io/en/latest/changelog.html
- PyPI: https://pypi.python.org/pypi/flask-marshmallow
- Issues: https://github.com/marshmallow-code/flask-marshmallow/issues

License
=======

MIT licensed. See the bundled `LICENSE <https://github.com/marshmallow-code/flask-marshmallow/blob/master/LICENSE>`_ file for more details.


.. _Flask: http://flask.pocoo.org
.. _marshmallow: http://marshmallow.readthedocs.io

.. |pypi-package| image:: https://badge.fury.io/py/flask-marshmallow.svg
    :target: http://badge.fury.io/py/flask-marshmallow
    :alt: Latest version
.. |build-status| image:: https://travis-ci.org/marshmallow-code/flask-marshmallow.svg?branch=pypi
    :target: https://travis-ci.org/marshmallow-code/flask-marshmallow
    :alt: Travis-CI
.. |coverage-status| image:: http://codecov.io/github/marshmallow-code/flask-marshmallow/coverage.svg?branch=dev
   :target: http://codecov.io/github/marshmallow-code/flask-marshmallow?branch=dev
   :alt: Test coverage
.. |docs| image:: https://readthedocs.org/projects/flask-marshmallow/badge/
   :target: http://flask-marshmallow.readthedocs.io/
   :alt: Documentation
