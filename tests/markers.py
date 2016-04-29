import pytest
import marshmallow
import flask
from distutils.version import LooseVersion


marshmallow_version = LooseVersion(marshmallow.__version__)
flask_version = LooseVersion(flask.__version__)


marshmallow_2_req = pytest.mark.skipif(
    marshmallow_version < LooseVersion("2.0"),
    reason="marshmallow 2.0 or higher required",
)

flask_1_req = pytest.mark.skipif(
    flask_version < LooseVersion("0.11"),
    reason="flask 0.11 or higher required",
)
