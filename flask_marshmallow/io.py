from webargs.flaskparser import parser
from flask import jsonify, current_app
from functools import wraps

# Flask config option; function that returns a response
_FORMATTER_CONFIG = 'MARSHMALLOW_RESPONSE_FORMATTER'

# Primitive implementation of marshal_with
# Doesn't handle tuple return values
# TODO: Replace with flask-smore's marshal_with
def marshal_with(schema):
    """View decorator for serializing a view's output to a response."""
    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            obj = func(*args, **kwargs)
            format_response = current_app.config.get(_FORMATTER_CONFIG, jsonify)
            return format_response(schema.dump(obj).data)
        return wrapped
    return decorator

def use_schema(schema, list_view=False, locations=None):
    """View decorator for using a marshmallow schema to
        (1) parse a request's input and
        (2) serializing the view's output to a response.
    """
    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            use_args_wrapper = parser.use_args(schema, locations=locations)
            # Function wrapped with use_args
            func_with_args = use_args_wrapper(func)
            ret = func_with_args(*args, **kwargs)
            # Serialize and jsonify the return value
            format_response = current_app.config.get(_FORMATTER_CONFIG, jsonify)
            return format_response(schema.dump(ret, many=list_view).data)
        return wrapped
    return decorator
