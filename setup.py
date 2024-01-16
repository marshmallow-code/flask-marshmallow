from setuptools import find_packages, setup

EXTRAS_REQUIRE = {
    "sqlalchemy": [
        "flask-sqlalchemy>=3.0.0",
        "marshmallow-sqlalchemy>=0.29.0",
    ],
    "docs": ["marshmallow-sqlalchemy>=0.19.0", "Sphinx==7.2.6", "sphinx-issues==3.0.1"],
}
EXTRAS_REQUIRE["tests"] = EXTRAS_REQUIRE["sqlalchemy"] + ["pytest"]
EXTRAS_REQUIRE["dev"] = EXTRAS_REQUIRE["tests"] + ["tox", "pre-commit~=3.5"]

REQUIRES = ["Flask", "marshmallow>=3.0.0", "packaging>=17.0"]


def read(fname):
    with open(fname) as fp:
        content = fp.read()
    return content


setup(
    name="flask-marshmallow",
    version="1.0.0",
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
    python_requires=">=3.8",
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    test_suite="tests",
    project_urls={
        "Issues": "https://github.com/marshmallow-code/flask-marshmallow/issues",
        "Funding": "https://opencollective.com/marshmallow",
    },
)
