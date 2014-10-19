*********************************************************
Flask-Marshmallow: Flask + marshmallow for beautiful APIs
*********************************************************

`github <http://github.com/sloria/flask-marshmallow>`_ //
`pypi <http://pypi.python.org/pypi/flask-marshmallow>`_ //
`issues <http://github.com/sloria/flask-marshmallow/issues>`_


Flask + marshmallow for beautiful APIs
======================================

Flask-Marshmallow is a thin integration layer for `Flask`_ (a Python web framework) and `marshmallow`_ (an object serialization/deserialization library) that adds additional features to marshmallow, including URL and Hyperlinks fields for HATEOAS-ready APIs.


Create your app.

.. code-block:: python

    from flask import Flask, jsonify
    from flask.ext.marshmallow import Marshmallow

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
            'self': ma.URL('author_detail', id='<id>'),
            'collection': ma.URL('authors')
        })


Output the data in your views.

.. code-block:: python

    @app.route('/api/users/')
    def users():
        all_users = User.all()
        result = users_schema.dump(all_users)
        return jsonify(result.data)

    @app.route('/api/users/<id>')
    def user_detail(id):
        user = User.get(id)
        result = user_schema.dump(user)
        return jsonify(result.data)
    # {
    #     "email": "fred@queen.com",
    #     "date_created": "Fri, 25 Apr 2014 06:02:56 -0000",
    #     "_links": {
    #         "self": "/api/authors/42",
    #         "collection": "/api/authors/"
    #     }
    # }


Learn More
==========

To learn more about marshmallow, check out its `docs <http://marshmallow.readthedocs.org/en/latest/>`_.


Get it now
==========

::

    pip install flask-marshmallow


Configuration
=============

The following app configuration values exist for Flask-Marshmallow.

+------------------------+------------------------------------------------------------------------------------------------------------------------------------+
| Config value           | Description                                                                                                                        |
+========================+====================================================================================================================================+
| MARSHMALLOW_STRICT     | Raise a :exc:`MarshallingError` if invalid data are passed to a `Schema` (instead of storing errors on the serializer object).     |
+------------------------+------------------------------------------------------------------------------------------------------------------------------------+
| MARSHMALLOW_DATEFORMAT | Default date format for all :class:`DateTime` fields. Can be a 'iso', 'rfc' or a date format string.                               |
+------------------------+------------------------------------------------------------------------------------------------------------------------------------+



API
===

.. automodule:: flask_marshmallow
    :inherited-members:


.. automodule:: flask_marshmallow.fields
    :members:


Useful Links
============

- `Flask docs`_
- `marshmallow docs`_

.. _marshmallow docs: http://marshmallow.readthedocs.org

.. _Flask docs: http://flask.pocoo.org/docs/

Project Info
============

.. toctree::
   :maxdepth: 1

   license
   changelog


.. _marshmallow: http://marshmallow.readthedocs.org

 .. _Flask: http://flask.pocoo.org
