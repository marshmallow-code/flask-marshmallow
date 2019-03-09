import pytest
import flask
from distutils.version import LooseVersion


flask_version = LooseVersion(flask.__version__)
flask_1_req = pytest.mark.skipif(
    flask_version < LooseVersion("0.11"), reason="flask 0.11 or higher required"
)
