Changelog
=========

1.2.0 (2024-02-05)
******************

Features:

* Performance improvement to `validate.FileSize` (:pr:`293`).
  Thanks :user:`uncle-lv`.

1.1.0 (2024-01-16)
******************

Features:

* Add type coverage (:pr:`290`).

1.0.0 (2024-01-16)
******************

Features:

* Add field ``fields.File``, ``validate.FileType``, and ``validate.FileSize`` 
  for deserializing uploaded files (:issue:`280`, :pr:`282`).
  Thanks :user:`uncle-lv` for the PR
* Add field ``Config`` for serializing Flask configuration values (:issue:`280`, :pr:`281`).
  Thanks :user:`greyli` for the PR.

Support:

* Support marshmallow-sqlalchemy>=0.29.0.
* Test against Python 3.12.
* Drop support for Python 3.7.

Other changes:

* *Backwards-incompatible*: Remove ```flask_marshmallow.__version__`` 
  and ``flask_marshmallow.__version_info__`` attributes (:pr:`284`). 
  Use feature detection or ``importlib.metadata.version("flask-marshmallow")`` instead.

0.15.0 (2023-04-05)
*******************

* Changes to supported software versions.

  * python3.6 or later and marshmallow>=3.0.0 are now required
  * Add support for python3.11
  * For ``sqlalchemy`` integration, marshmallow-sqlalchemy>=0.28.2 and
    flask-sqlalchemy>=3.0.0 are now required

* *Backwards-incompatible*: ``URLFor`` and ``AbsoluteURLFor`` now do not accept
  parameters for ``flask.url_for`` as top-level parameters. They must always be
  passed in the ``values`` dictionary, as explained in the v0.14.0 changelog.

Bug fixes:

* Address distutils deprecation warning in Python 3.10 (:pr:`242`).
  Thanks :user:`GabrielLins64` for the PR.

0.14.0 (2020-09-27)
*******************

* Add ``values`` argument to ``URLFor`` and ``AbsoluteURLFor`` for passing values to ``flask.url_for``.
  This prevents unrelated parameters from getting passed (:issue:`52`, :issue:`67`).
  Thanks :user:`AlrasheedA` for the PR.

Deprecation:

* Passing params to ``flask.url_for`` via ``URLFor``'s and ``AbsoluteURLFor``'s constructor
  params is deprecated. Pass ``values`` instead.

.. code-block:: python

    # flask-marshmallow<0.14.0


    class UserSchema(ma.Schema):
        _links = ma.Hyperlinks(
            {
                "self": ma.URLFor("user_detail", id="<id>"),
            }
        )


    # flask-marshmallow>=0.14.0


    class UserSchema(ma.Schema):
        _links = ma.Hyperlinks(
            {
                "self": ma.URLFor("user_detail", values=dict(id="<id>")),
            }
        )

0.13.0 (2020-06-07)
*******************

Bug fixes:

* Fix compatibility with marshmallow-sqlalchemy<0.22.0 (:issue:`189`).
  Thanks :user:`PatrickRic` for reporting.

Other changes:

* Remove unused ``flask_marshmallow.sqla.SchemaOpts``.

0.12.0 (2020-04-26)
*******************

* *Breaking change*: ``ma.ModelSchema`` and ``ma.TableSchema`` are removed, since these are deprecated upstream.

.. warning::
  It is highly recommended that you use the newer ``ma.SQLAlchemySchema`` and ``ma.SQLAlchemyAutoSchema``  classes
  instead of ``ModelSchema`` and ``TableSchema``. See the release notes for `marshmallow-sqlalchemy 0.22.0 <https://marshmallow-sqlalchemy.readthedocs.io/en/latest/changelog.html>`_
  for instructions on how to migrate.

If you need to use ``ModelSchema`` and ``TableSchema`` for the time being, you'll need to import these directly from ``marshmallow_sqlalchemy``.

.. code-block:: python

    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    from flask_marshmallow import Marshmallow

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/test.db"

    db = SQLAlchemy(app)
    ma = Marshmallow(app)

    # flask-marshmallow<0.12.0


    class AuthorSchema(ma.ModelSchema):
        class Meta:
            model = Author


    # flask-marshmallow>=0.12.0 (recommended)


    class AuthorSchema(ma.SQLAlchemyAutoSchema):
        class Meta:
            model = Author
            load_instance = True


    # flask-marshmallow>=0.12.0 (not recommended)

    from marshmallow_sqlalchemy import ModelSchema


    class AuthorSchema(ModelSchema):
        class Meta:
            model = Author
            sql_session = db.session

Bug fixes:

* Fix binding Flask-SQLAlchemy's scoped session to ``ma.SQLAlchemySchema`` and ``ma.SQLAlchemyAutoSchema``.
  (:issue:`180`). Thanks :user:`fnalonso` for reporting.

0.11.0 (2020-02-09)
*******************

Features:

* Add support for ``SQLAlchemySchema``, ``SQLAlchemyAutoSchema``, and ``auto_field``
  from marshmallow-sqlalchemy>=0.22.0 (:pr:`166`).

Bug fixes:

* Properly restrict marshmallow-sqlalchemy version based on Python version (:pr:`158`).

Other changes:

* Test against Python 3.8.

0.10.1 (2019-05-05)
*******************

Bug fixes:

* marshmallow 3.0.0rc6 compatibility (:pr:`134`).

0.10.0 (2019-03-09)
*******************

Features:

* Add `ma.TableSchema` (:pr:`124`).
* SQLAlchemy requirements can be installed with ``pip install
  'flask-marshmallow[sqlalchemy]'``.


Bug fixes:

* ``URLFor``, ``AbsoluteURLFor``, and ``HyperlinkRelated`` serialize to ``None`` if a passed attribute value is ``None`` (:issue:`18`, :issue:`68`, :pr:`72`).
  Thanks :user:`RobinRamuel`, :user:`ocervell`, and :user:`feigner` for reporting.

Support:

* Test against Python 3.7.
* Drop support for Python 3.4. Only Python 2.7 and >=3.5 are supported.

0.9.0 (2018-04-29)
******************

* Add support for marshmallow 3 beta. Thanks :user:`SBillion` for the PR.
* Drop support for Python 3.3. Only Python 2.7 and >=3.4 are supported.
* Updated documentation to fix example ``ma.URLFor`` target.

0.8.0 (2017-05-28)
******************

* Fix compatibility with marshmallow>=3.0.

Support:

* *Backwards-incompatible*: Drop support for marshmallow<=2.0.0.
* Test against Python 3.6.

0.7.0 (2016-06-28)
******************

* ``many`` argument to ``Schema.jsonify`` defaults to value of the ``Schema`` instance's ``many`` attribute (:issue:`42`). Thanks :user:`singingwolfboy`.
* Attach `HyperlinkRelated` to `Marshmallow` instances. Thanks :user:`singingwolfboy` for reporting.

Support:

* Upgrade to invoke>=0.13.0.
* Updated documentation to reference `HyperlinkRelated` instead of `HyperlinkModelSchema`. Thanks :user:`singingwolfboy`.
* Updated documentation links to readthedocs.io subdomain. Thanks :user:`adamchainz`.

0.6.2 (2015-09-16)
******************

* Fix compatibility with marshmallow>=2.0.0rc2.

Support:

* Tested against Python 3.5.

0.6.1 (2015-09-06)
******************

* Fix compatibility with marshmallow-sqlalchemy>=0.4.0 (:issue:`25`). Thanks :user:`svenstaro` for reporting.

Support:

* Include docs in release tarballs.

0.6.0 (2015-05-02)
******************

Features:

- Add Flask-SQLAlchemy/marshmallow-sqlalchemy support via the ``ModelSchema`` and ``HyperlinkModelSchema`` classes.
- ``Schema.jsonify`` now takes the same arguments as ``marshmallow.Schema.dump``. Additional keyword arguments are passed to ``flask.jsonify``.
- ``Hyperlinks`` field supports serializing a list of hyperlinks (:issue:`11`). Thanks :user:`royrusso` for the suggestion.


Deprecation/Removal:

- Remove support for ``MARSHMALLOW_DATEFORMAT`` and ``MARSHMALLOW_STRICT`` config options.

Other changes:

- Drop support for marshmallow<1.2.0.

0.5.1 (2015-04-27)
******************

* Fix compatibility with marshmallow>=2.0.0.

0.5.0 (2015-03-29)
******************

* *Backwards-incompatible*: Remove ``flask_marshmallow.SchemaOpts`` class and remove support for ``MARSHMALLOW_DATEFORMAT`` and ``MARSHMALLOW_STRICT`` (:issue:`8`). Prevents a ``RuntimeError`` when instantiating a ``Schema`` outside of a request context.

0.4.0 (2014-12-22)
******************

* *Backwards-incompatible*: Rename ``URL`` and ``AbsoluteURL`` to ``URLFor`` and ``AbsoluteURLFor``, respectively, to prevent overriding marshmallow's ``URL`` field (:issue:`6`). Thanks :user:`svenstaro` for the suggestion.
* Fix bug that raised an error when deserializing ``Hyperlinks`` and ``URL`` fields (:issue:`9`). Thanks :user:`raj-kesavan` for reporting.

Deprecation:

* ``Schema.jsonify`` is deprecated. Use ``flask.jsonify`` on the result of ``Schema.dump`` instead.
* The ``MARSHMALLOW_DATEFORMAT`` and ``MARSHMALLOW_STRICT`` config values are deprecated. Use a base ``Schema`` class instead (:issue:`8`).

0.3.0 (2014-10-19)
******************

* Supports marshmallow >= 1.0.0-a.

0.2.0 (2014-05-12)
******************

* Implementation as a proper class-based Flask extension.
* Serializer and fields classes are available from the ``Marshmallow`` object.

0.1.0 (2014-04-25)
******************

* First release.
* ``Hyperlinks``, ``URL``, and ``AbsoluteURL`` fields implemented.
* ``Serializer#jsonify`` implemented.
