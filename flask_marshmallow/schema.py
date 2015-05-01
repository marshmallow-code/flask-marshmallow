# -*- coding: utf-8 -*-
import flask
import marshmallow as ma

class Schema(ma.Schema):
    """Base serializer with which to define custom serializers.

    See `marshmallow.Schema` for more details about the `Schema` API.
    """

    def jsonify(self, obj, many=False, *args, **kwargs):
        """Return a JSON response containing the serialized data.


        :param obj: Object to serialize.
        :param bool many: Set to `True` if `obj` should be serialized as a collection.
        :param kwargs: Additional keyword arguments passed to `flask.jsonify`.

        .. versionchanged:: 0.6.0
            Takes the same arguments as `marshmallow.Schema.dump`. Additional
            keyword arguments are passed to `flask.jsonify`.
        """
        data = self.dump(obj, many=many).data
        return flask.jsonify(data, *args, **kwargs)
