Changelog
=========

0.4.0 (2014-12-22)
******************

* *Backwards-incompatible*: Rename ``URL`` and ``AbsoluteURL`` to ``URLFor`` and ``AbsoluteURLFor``, respectively, to prevent overriding marshmallow's ``URL`` field. Thanks @svenstaro for the suggestion.
* Fix bug that raised an error when deserializing ``Hyperlinks`` and ``URL`` fields. Thanks @raj-kesavan for reporting.

Deprecation:

* ``Schema.jsonify`` is deprecated. Use ``flask.jsonify`` on the result of ``Schema.dump`` instead.
* The ``MARSHMALLOW_DATEFORMAT`` and ``MARSHMALLOW_STRICT`` config values are deprecated. Use a base ``Schema`` class instead.

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
