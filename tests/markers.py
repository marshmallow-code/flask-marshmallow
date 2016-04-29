import pytest
import marshmallow


marshmallow_2_req = pytest.mark.skipif(
    int(marshmallow.__version__.split('.')[0]) < 2,
    reason="marshmallow 2.0 or higher required",
)
