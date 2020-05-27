# -*- coding: utf-8 -*-
import re
from setuptools import setup, find_packages


EXTRAS_REQUIRE = {
    "sqlalchemy": [
        "flask-sqlalchemy",
        'marshmallow-sqlalchemy>=0.13.0; python_version >= "3.6"',
        'marshmallow-sqlalchemy>=0.13.0,<0.19.0; python_version < "3.6"',
    ],
    "docs": ["marshmallow-sqlalchemy>=0.13.0", "Sphinx==3.0.4", "sphinx-issues==1.2.0"],
    "lint": [
        "flake8==3.8.2",
        'flake8-bugbear==20.1.4; python_version >= "3.5"',
        "pre-commit~=2.4",
    ],
}
EXTRAS_REQUIRE["tests"] = EXTRAS_REQUIRE["sqlalchemy"] + ["pytest", "mock"]
EXTRAS_REQUIRE["dev"] = EXTRAS_REQUIRE["tests"] + EXTRAS_REQUIRE["lint"] + ["tox"]

REQUIRES = ["Flask", "marshmallow>=2.0.0", "six>=1.9.0"]


def find_version(fname):
    """Attempts to find the version number in the file names fname.
    Raises RuntimeError if not found.
    """
    version = ""
    with open(fname, "r") as fp:
        reg = re.compile(r'__version__ = [\'"]([^\'"]*)[\'"]')
        for line in fp:
            m = reg.match(line)
            if m:
                version = m.group(1)
                break
    if not version:
        raise RuntimeError("Cannot find version information")
    return version


def read(fname):
    with open(fname) as fp:
        content = fp.read()
    return content


setup(
    name="flask-marshmallow",
    version=find_version("src/flask_marshmallow/__init__.py"),
    description="Flask + marshmallow for beautiful APIs",
    long_description=read("README.rst"),
    author="Steven Loria",
    author_email="sloria1@gmail.com",
    url="https://github.com/marshmallow-code/flask-marshmallow",
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    license="MIT",
    zip_safe=False,
    keywords="flask-marshmallow",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    test_suite="tests",
    project_urls={
        "Issues": "https://github.com/marshmallow-code/flask-marshmallow/issues",
        "Funding": "https://opencollective.com/marshmallow",
    },
)
