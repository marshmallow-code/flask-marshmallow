from marshmallow import ValidationError

from flask_marshmallow.compat import _MARSHMALLOW_VERSION_INFO


def get_dump_data(schema, obj):
    if _MARSHMALLOW_VERSION_INFO[0] >= 3:
        return schema.dump(obj)

    return schema.dump(obj).data


def get_load_data(schema, obj):
    if _MARSHMALLOW_VERSION_INFO[0] >= 3:
        try:
            return schema.load(obj), None
        except ValidationError as err:
            return None, err.normalized_messages()

    return schema.load(obj).data, schema.load(obj).errors
