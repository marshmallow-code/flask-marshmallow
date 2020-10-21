from marshmallow import ValidationError


def get_dump_data(schema, obj):
    return schema.dump(obj)


def get_load_data(schema, obj):
    try:
        return schema.load(obj), None
    except ValidationError as err:
        return None, err.normalized_messages()
