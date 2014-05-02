*********************************************************
Flask-Marshmallow: Flask + marshmallow for beautiful APIs
*********************************************************

`github <http://github.com/sloria/flask-marshmallow>`_ //
`pypi <http://pypi.python.org/pypi/flask-marshmallow>`_ //
`issues <http://github.com/sloria/flask-marshmallow/issues>`_


Flask + marshmallow for beautiful APIs
======================================

Flask-Marshmallow is a thin integration layer for `Flask`_ (a Python web framework) and `marshmallow`_ (a serialization library) that adds additional features to marshmallow, including URL and Hyperlinks fields for HATEOAS-ready APIs.

.. code-block:: python

    from flask import Flask
    from your_orm import Model, Column, Integer, String, DateTime
    from flask.ext.marshmallow import Marshmallow, pprint

    app = Flask(__name__)
    ma = Marshmallow(app)

    class User(Model):
        email = Column(String)
        password = Column(String)
        date_created = Column(DateTime, auto_now_add=True)

    class UserMarshal(ma.Serializer):
        class Meta:
            # Fields to expose
            fields = ('email', 'date_created', '_links')

        _links = ma.Hyperlinks({
            'self': ma.URL('author_detail', id='<id>'),
            'collection': ma.URL('authors')
        })

    user = User(email='fred@queen.com', password='secret')
    user.save()

    serialized = UserMarshal(user)
    pprint(serialized.data)
    # {
    #     "email": "fred@queen.com",
    #     "date_created": "Fri, 25 Apr 2014 06:02:56 -0000",
    #     "_links": {
    #         "self": "/api/authors/42",
    #         "collection": "/api/authors/"
    #     }
    # }

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
| MARSHMALLOW_STRICT     | Raise a :class:`MarshallingError` if invalid data are passed to a serializer (instead of storing errors on the serializer object). |
+------------------------+------------------------------------------------------------------------------------------------------------------------------------+
| MARSHMALLOW_DATEFORMAT | Default date format for all :class:`DateTime` fields.                                                                              |
+------------------------+------------------------------------------------------------------------------------------------------------------------------------+



API
===

.. module:: flask_marshmallow

.. autoclass:: flask_marshmallow.Marshmallow
    :members:


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
