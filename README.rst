*****************
Flask-Marshmallow
*****************

.. image:: https://travis-ci.org/sloria/flask-marshmallow.png?branch=master
        :target: https://travis-ci.org/sloria/flask-marshmallow


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

http://flask-marshmallow.readthedocs.org/
=========================================

License
=======

MIT licensed. See the bundled `LICENSE <https://github.com/sloria/flask-marshmallow/blob/master/LICENSE>`_ file for more details.


.. _Flask: http://flask.pocoo.org
.. _marshmallow: http://marshmallow.readthedocs.org

