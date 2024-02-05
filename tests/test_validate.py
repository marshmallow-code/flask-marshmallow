import io

import pytest
from marshmallow.exceptions import ValidationError
from werkzeug.datastructures import FileStorage

from flask_marshmallow import validate


@pytest.mark.parametrize("size", ["1 KB", "1 KiB", "1 MB", "1 MiB", "1 GB", "1 GiB"])
def test_parse_size(size):
    rv = validate._parse_size(size)
    if size == "1 KB":
        assert rv == 1000
    elif size == "1 KiB":
        assert rv == 1024
    elif size == "1 MB":
        assert rv == 1000000
    elif size == "1 MiB":
        assert rv == 1048576
    elif size == "1 GB":
        assert rv == 1000000000
    elif size == "1 GiB":
        assert rv == 1073741824


def test_get_filestorage_size():
    rv = validate._get_filestorage_size(FileStorage(io.BytesIO(b"".ljust(0))))
    assert rv == 0
    rv = validate._get_filestorage_size(FileStorage(io.BytesIO(b"".ljust(123))))
    assert rv == 123
    rv = validate._get_filestorage_size(FileStorage(io.BytesIO(b"".ljust(1024))))
    assert rv == 1024
    rv = validate._get_filestorage_size(FileStorage(io.BytesIO(b"".ljust(1234))))
    assert rv == 1234


@pytest.mark.parametrize("size", ["wrong_format", "1.2.3 MiB"])
def test_parse_size_wrong_value(size):
    if size == "wrong_format":
        with pytest.raises(ValueError, match="Invalid size value: "):
            validate._parse_size(size)
    elif size == "1.2.3 MiB":
        with pytest.raises(
            ValueError, match="Invalid float value while parsing size: "
        ):
            validate._parse_size(size)


def test_filesize_min():
    fs = FileStorage(io.BytesIO(b"".ljust(1024)))
    assert validate.FileSize(min="1 KiB", max="2 KiB")(fs) is fs
    assert validate.FileSize(min="0 KiB", max="1 KiB")(fs) is fs
    assert validate.FileSize()(fs) is fs
    assert validate.FileSize(min_inclusive=False, max_inclusive=False)(fs) is fs
    assert validate.FileSize(min="1 KiB", max="1 KiB")(fs) is fs

    with pytest.raises(ValidationError, match="Must be greater than or equal to 2 KiB"):
        validate.FileSize(min="2 KiB", max="3 KiB")(fs)
    with pytest.raises(ValidationError, match="Must be greater than or equal to 2 KiB"):
        validate.FileSize(min="2 KiB")(fs)
    with pytest.raises(ValidationError, match="Must be greater than 1 KiB"):
        validate.FileSize(
            min="1 KiB", max="2 KiB", min_inclusive=False, max_inclusive=True
        )(fs)
    with pytest.raises(ValidationError, match="less than 1 KiB"):
        validate.FileSize(
            min="1 KiB", max="1 KiB", min_inclusive=True, max_inclusive=False
        )(fs)


def test_filesize_max():
    fs = FileStorage(io.BytesIO(b"".ljust(2048)))
    assert validate.FileSize(min="1 KiB", max="2 KiB")(fs) is fs
    assert validate.FileSize(max="2 KiB")(fs) is fs
    assert validate.FileSize()(fs) is fs
    assert validate.FileSize(min_inclusive=False, max_inclusive=False)(fs) is fs
    assert validate.FileSize(min="2 KiB", max="2 KiB")(fs) is fs

    with pytest.raises(ValidationError, match="less than or equal to 1 KiB"):
        validate.FileSize(min="0 KiB", max="1 KiB")(fs)
    with pytest.raises(ValidationError, match="less than or equal to 1 KiB"):
        validate.FileSize(max="1 KiB")(fs)
    with pytest.raises(ValidationError, match="less than 2 KiB"):
        validate.FileSize(
            min="1 KiB", max="2 KiB", min_inclusive=True, max_inclusive=False
        )(fs)
    with pytest.raises(ValidationError, match="greater than 2 KiB"):
        validate.FileSize(
            min="2 KiB", max="2 KiB", min_inclusive=False, max_inclusive=True
        )(fs)


def test_filesize_repr():
    assert (
        repr(
            validate.FileSize(
                min=None, max=None, error=None, min_inclusive=True, max_inclusive=True
            )
        )
        == "<FileSize(min=None, max=None, min_inclusive=True, max_inclusive=True, error=None)>"  # noqa: E501
    )

    assert (
        repr(
            validate.FileSize(
                min="1 KiB",
                max="3 KiB",
                error="foo",
                min_inclusive=False,
                max_inclusive=False,
            )
        )
        == "<FileSize(min='1 KiB', max='3 KiB', min_inclusive=False, max_inclusive=False, error='foo')>"  # noqa: E501
    )


def test_filesize_wrongtype():
    with pytest.raises(TypeError, match="A FileStorage object is required, not "):
        validate.FileSize()(1)


def test_filetype():
    png_fs = FileStorage(io.BytesIO(b"".ljust(1024)), "test.png")
    assert validate.FileType([".png"])(png_fs) is png_fs
    assert validate.FileType([".PNG"])(png_fs) is png_fs

    PNG_fs = FileStorage(io.BytesIO(b"".ljust(1024)), "test.PNG")
    assert validate.FileType([".png"])(PNG_fs) is PNG_fs
    assert validate.FileType([".PNG"])(PNG_fs) is PNG_fs

    with pytest.raises(TypeError, match="A FileStorage object is required, not "):
        validate.FileType([".png"])(1)

    with pytest.raises(
        ValidationError,
        match=r"Not an allowed file type. Allowed file types: \[.*?\]",  # noqa: W605
    ):
        jpg_fs = FileStorage(io.BytesIO(b"".ljust(1024)), "test.jpg")
        validate.FileType([".png"])(jpg_fs)

    with pytest.raises(
        ValidationError,
        match=r"Not an allowed file type. Allowed file types: \[.*?\]",  # noqa: W605
    ):
        no_ext_fs = FileStorage(io.BytesIO(b"".ljust(1024)), "test")
        validate.FileType([".png"])(no_ext_fs)
