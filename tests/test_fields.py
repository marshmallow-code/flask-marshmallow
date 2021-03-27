from datetime import date, timedelta

from flask import current_app, url_for
from marshmallow import ValidationError
from werkzeug.routing import BuildError
import pytest
from flask_marshmallow.fields import _tpl


@pytest.mark.parametrize(
    "template", ["<id>", " <id>", "<id> ", "< id>", "<id  >", "< id >"]
)
def test_tpl(template):
    assert _tpl(template) == "id"
    assert _tpl(template) == "id"
    assert _tpl(template) == "id"


def test_url_field(ma, mockauthor):
    field = ma.URLFor("author", id="<id>")
    result = field.serialize("url", mockauthor)
    assert result == url_for("author", id=mockauthor.id)

    field = ma.URLFor("author", values=dict(id="<id>"))
    result = field.serialize("url", mockauthor)
    assert result == url_for("author", id=mockauthor.id)

    mockauthor.id = 0
    result = field.serialize("url", mockauthor)
    assert result == url_for("author", id=0)


def test_url_field_with_invalid_attribute(ma, mockauthor):
    field = ma.URLFor("author", id="<not-an-attr>")
    expected_msg = "{!r} is not a valid attribute of {!r}".format(
        "not-an-attr", mockauthor
    )
    with pytest.raises(AttributeError, match=expected_msg):
        field.serialize("url", mockauthor)

    field = ma.URLFor("author", values=dict(id="<not-an-attr>"))
    expected_msg = "{!r} is not a valid attribute of {!r}".format(
        "not-an-attr", mockauthor
    )
    with pytest.raises(AttributeError, match=expected_msg):
        field.serialize("url", mockauthor)


def test_url_field_handles_nested_attribute(ma, mockbook, mockauthor):
    field = ma.URLFor("author", id="<author.id>")
    result = field.serialize("url", mockbook)
    assert result == url_for("author", id=mockauthor.id)

    field = ma.URLFor("author", values=dict(id="<author.id>"))
    result = field.serialize("url", mockbook)
    assert result == url_for("author", id=mockauthor.id)


def test_url_field_handles_none_attribute(ma, mockbook, mockauthor):
    mockbook.author = None

    field = ma.URLFor("author", id="<author>")
    result = field.serialize("url", mockbook)
    assert result is None

    field = ma.URLFor("author", id="<author.id>")
    result = field.serialize("url", mockbook)
    assert result is None

    field = ma.URLFor("author", values=dict(id="<author>"))
    result = field.serialize("url", mockbook)
    assert result is None

    field = ma.URLFor("author", values=dict(id="<author.id>"))
    result = field.serialize("url", mockbook)
    assert result is None


def test_url_field_deserialization(ma):
    field = ma.URLFor("author", id="<not-an-attr>", allow_none=True)
    # noop
    assert field.deserialize("foo") == "foo"
    assert field.deserialize(None) is None

    field = ma.URLFor("author", values=dict(id="<not-an-attr>"), allow_none=True)
    # noop
    assert field.deserialize("foo") == "foo"
    assert field.deserialize(None) is None


def test_invalid_endpoint_raises_build_error(ma, mockauthor):
    field = ma.URLFor("badendpoint")
    with pytest.raises(BuildError):
        field.serialize("url", mockauthor)


def test_hyperlinks_field(ma, mockauthor):
    field = ma.Hyperlinks(
        {"self": ma.URLFor("author", id="<id>"), "collection": ma.URLFor("authors")}
    )

    result = field.serialize("_links", mockauthor)
    assert result == {
        "self": url_for("author", id=mockauthor.id),
        "collection": url_for("authors"),
    }


def test_hyperlinks_field_recurses(ma, mockauthor):
    field = ma.Hyperlinks(
        {
            "self": {"href": ma.URLFor("author", id="<id>"), "title": "The author"},
            "collection": {"href": ma.URLFor("authors"), "title": "Authors list"},
        }
    )
    result = field.serialize("_links", mockauthor)

    assert result == {
        "self": {"href": url_for("author", id=mockauthor.id), "title": "The author"},
        "collection": {"href": url_for("authors"), "title": "Authors list"},
    }


def test_hyperlinks_field_recurses_into_list(ma, mockauthor):
    field = ma.Hyperlinks(
        [
            {"rel": "self", "href": ma.URLFor("author", id="<id>")},
            {"rel": "collection", "href": ma.URLFor("authors")},
        ]
    )
    result = field.serialize("_links", mockauthor)

    assert result == [
        {"rel": "self", "href": url_for("author", id=mockauthor.id)},
        {"rel": "collection", "href": url_for("authors")},
    ]


def test_hyperlinks_field_deserialization(ma):
    field = ma.Hyperlinks({"href": ma.URLFor("author", id="<id>")}, allow_none=True)
    # noop
    assert field.deserialize("/author") == "/author"
    assert field.deserialize(None) is None


def test_absolute_url(ma, mockauthor):
    field = ma.AbsoluteURLFor("authors")
    result = field.serialize("abs_url", mockauthor)
    assert result == url_for("authors", _external=True)


def test_absolute_url_deserialization(ma):
    field = ma.AbsoluteURLFor("authors", allow_none=True)
    assert field.deserialize("foo") == "foo"
    assert field.deserialize(None) is None


def test_aliases(ma):
    from flask_marshmallow.fields import UrlFor, AbsoluteUrlFor, URLFor, AbsoluteURLFor

    assert UrlFor is URLFor
    assert AbsoluteUrlFor is AbsoluteURLFor


@pytest.mark.usefixtures("app")
class TestFlaskConfig:
    def test_unbound(self, ma):
        assert ma.FlaskConfig().config_name is None

    def test_copy_inner_on_bind(self, ma):
        # binding creates copies
        inner = ma.String()
        field = ma.FlaskConfig(inner)
        field._bind_to_schema("field_name", ma.Schema())
        assert field.inner is not inner

    def test_defaults(self, ma):
        class TestSchema(ma.Schema):
            # defaults: use field name as ACME_FOO, type String
            acme_foo = ma.FlaskConfig()

            # only specify field type
            acme_bar = ma.FlaskConfig(ma.Integer)

            # specify both
            monty = ma.FlaskConfig(
                ma.TimeDelta(precision=ma.TimeDelta.MINUTES), "ACME_MONTY_PYTHON_OFFSET"
            )

        schema = TestSchema()

        foo = schema.fields["acme_foo"]
        assert isinstance(foo.inner, ma.String)
        assert foo.config_name == "ACME_FOO"

        bar = schema.fields["acme_bar"]
        assert isinstance(bar.inner, ma.Integer)
        assert bar.config_name == "ACME_BAR"

        monty = schema.fields["monty"]
        assert isinstance(monty.inner, ma.TimeDelta)
        assert monty.config_name == "ACME_MONTY_PYTHON_OFFSET"

        current_app.config.update(
            {
                "ACME_FOO": "foo_value",
                "ACME_BAR": 42,
                "ACME_MONTY_PYTHON_OFFSET": timedelta(minutes=17, seconds=23),
            }
        )

        data = schema.dump({})
        assert data == {
            "acme_foo": "foo_value",
            "acme_bar": 42,
            "monty": 17,
        }

    def test_nested(self, ma):
        class AcmeNested(ma.Schema):
            spam = ma.String()
            ham = ma.Date()

        class TestSchema(ma.Schema):
            vikings = ma.FlaskConfig(ma.Nested(AcmeNested), "ACME_VIKING_CONFIG")

        current_app.config.update(
            {
                "ACME_VIKING_CONFIG": {
                    "spam": "spam spam spam spam",
                    "ham": date(1970, 12, 15),
                },
            }
        )
        data = TestSchema().dump({})
        assert data == {"vikings": {"spam": "spam spam spam spam", "ham": "1970-12-15"}}

    @pytest.mark.parametrize(
        "field_kwargs", ({"only": ("ham",)}, {"exclude": ("spam",)})
    )
    def test_nested_field_config(self, ma, field_kwargs):
        class AcmeNested(ma.Schema):
            spam = ma.String()
            ham = ma.Date()

        class TestSchema(ma.Schema):
            vikings = ma.FlaskConfig(
                ma.Nested(AcmeNested, **field_kwargs), "ACME_VIKING_CONFIG"
            )

        current_app.config.update(
            {
                "ACME_VIKING_CONFIG": {
                    "spam": "spam spam spam spam",
                    "ham": date(1970, 12, 15),
                },
            }
        )
        data = TestSchema().dump({})
        assert data == {"vikings": {"ham": "1970-12-15"}}

    @pytest.mark.parametrize(
        "schema_kwargs", ({"only": ("vikings.ham",)}, {"exclude": ("vikings.spam",)})
    )
    def test_nested_schema_config(self, ma, schema_kwargs):
        class AcmeNested(ma.Schema):
            spam = ma.String()
            ham = ma.Date()

        class TestSchema(ma.Schema):
            vikings = ma.FlaskConfig(ma.Nested(AcmeNested), "ACME_VIKING_CONFIG")

        current_app.config.update(
            {
                "ACME_VIKING_CONFIG": {
                    "spam": "spam spam spam spam",
                    "ham": date(1970, 12, 15),
                },
            }
        )
        data = TestSchema(**schema_kwargs).dump({})
        assert data == {"vikings": {"ham": "1970-12-15"}}

    def test_dump_only_default(self, ma):
        class TestSchema(ma.Schema):
            foo = ma.FlaskConfig(config_name="ACME_FOO")

        data = {"foo": "incoming value"}
        current_app.config["ACME_FOO"] = "current value"
        with pytest.raises(ValidationError) as context:
            TestSchema().load(data)
        assert "foo" in context.value.messages
        assert current_app.config["ACME_FOO"] == "current value"

    def test_dump_only_false(self, ma):
        class TestSchema(ma.Schema):
            foo = ma.FlaskConfig(config_name="ACME_FOO", dump_only=False)

        data = {"foo": "incoming value"}
        current_app.config["ACME_FOO"] = "current value"
        deser = TestSchema().load(data)
        assert current_app.config["ACME_FOO"] == "incoming value"
        assert deser == {}
