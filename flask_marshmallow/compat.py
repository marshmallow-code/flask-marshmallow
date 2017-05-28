"""Compatibility module.

This module should be considered private API.
"""
import marshmallow
from marshmallow.utils import get_value as _get_value

_MARSHMALLOW_VERSION_INFO = tuple(
    [int(part) for part in marshmallow.__version__.split('.') if part.isdigit()]
)

# marshmallow>=3.0 switches the order of the obj and attr arguments from previous versions
if _MARSHMALLOW_VERSION_INFO[0] >= 3:
    get_value = _get_value
else:
    def get_value(obj, attr, *args, **kwargs):
        return _get_value(attr, obj, *args, **kwargs)
