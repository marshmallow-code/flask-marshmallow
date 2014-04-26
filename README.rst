*****************
Flask-Marshmallow
*****************

.. image:: https://travis-ci.org/sloria/flask-marshmallow.png?branch=master
        :target: https://travis-ci.org/sloria/flask-marshmallow


Flask + marshmallow for beautiful APIs
======================================

*Flask-Marshmallow is a thin integration layer for Flask and marshmallow that adds additional features to marshmallow, including URL and Hyperlinks fields for HATEOAS-ready APIs.*


.. code-block:: python

    from myapp.database import Model, Integer, String, DateTime
    from flask_marshmallow import Serializer, fields, pprint

    class User(Model):
        id = Column(Integer)
        email = Column(String)
        password = Column(String)
        date_created = Column(DateTime, auto_now_add=True)

    class UserMarshal(Serializer):

        class Meta:
            # Fields to expose
            fields = ('email', 'date_created', '_links')

        _links = fields.Hyperlinks({
            # Same params as Flask.url_for, but args can be attribute names
            # surrounded by < >
            'self': fields.URL('author_detail', id='<id>'),
            'collection': fields.URL('authors')
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
