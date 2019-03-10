"""Compatibility module.

This module should be considered private API.
"""
import marshmallow

_MARSHMALLOW_VERSION_INFO = tuple(
    [int(part) for part in marshmallow.__version__.split(".") if part.isdigit()]
)
