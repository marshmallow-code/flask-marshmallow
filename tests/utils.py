from flask_marshmallow.compat import _MARSHMALLOW_VERSION_INFO

def get_dump_data(schema, obj):
    if _MARSHMALLOW_VERSION_INFO[0] >= 3:
        return schema.dump(obj)

    return schema.dump(obj).data

def get_load_data(schema, obj):
    if _MARSHMALLOW_VERSION_INFO[0] >= 3:
        return schema.load(obj)
    return schema.load(obj).data