import pytest
import flask
from packaging.version import Version


flask_version = Version(flask.__version__)
flask_1_req = pytest.mark.skipif(
    flask_version < Version("0.11"), reason="flask 0.11 or higher required"
)
