# -*- coding: utf-8 -*-
import flask
import marshmallow as ma

from flask_marshmallow.compat import _MARSHMALLOW_VERSION_INFO

sentinel = object()


class Schema(ma.Schema):
    """Base serializer with which to define custom serializers.

    See `marshmallow.Schema` for more details about the `Schema` API.
    """

    def jsonify(self, obj, many=sentinel, *args, **kwargs):
        """Return a JSON response containing the serialized data.


        :param obj: Object to serialize.
        :param bool many: Whether `obj` should be serialized as an instance
            or as a collection. If unset, defaults to the value of the
            `many` attribute on this Schema.
        :param kwargs: Additional keyword arguments passed to `flask.jsonify`.

        .. versionchanged:: 0.6.0
            Takes the same arguments as `marshmallow.Schema.dump`. Additional
            keyword arguments are passed to `flask.jsonify`.

        .. versionchanged:: 0.6.3
            The `many` argument for this method defaults to the value of
            the `many` attribute on the Schema. Previously, the `many`
            argument of this method defaulted to False, regardless of the
            value of `Schema.many`.
        """
        if many is sentinel:
            many = self.many
        if _MARSHMALLOW_VERSION_INFO[0] >= 3:
            data = self.dump(obj, many=many)
        else:
            data = self.dump(obj, many=many).data
        return flask.jsonify(data, *args, **kwargs)
