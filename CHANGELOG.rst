Changelog
=========

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
