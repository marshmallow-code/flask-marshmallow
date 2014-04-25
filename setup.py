# -*- coding: utf-8 -*-
import re
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


REQUIRES = [
    'Flask',
    'marshmallow>=0.5.4',
]

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


def find_version(fname):
    '''Attempts to find the version number in the file names fname.
    Raises RuntimeError if not found.
    '''
    version = ''
    with open(fname, 'r') as fp:
        reg = re.compile(r'__version__ = [\'"]([^\'"]*)[\'"]')
        for line in fp:
            m = reg.match(line)
            if m:
                version = m.group(1)
                break
    if not version:
        raise RuntimeError('Cannot find version information')
    return version

__version__ = find_version("flask_marshmallow/__init__.py")


def read(fname):
    with open(fname) as fp:
        content = fp.read()
    return content

setup(
    name='flask-marshmallow',
    version=__version__,
    description='Flask + marshmallow for beautiful APIs',
    long_description=(read("README.rst") + '\n\n' +
                        read("HISTORY.rst")),
    author='Steven Loria',
    author_email='sloria1@gmail.com',
    url='https://github.com/sloria/flask-marshmallow',
    packages=find_packages(exclude=("test*", )),
    package_dir={'flask-marshmallow': 'flask-marshmallow'},
    include_package_data=True,
    install_requires=REQUIRES,
    license=read("LICENSE"),
    zip_safe=False,
    keywords='flask-marshmallow',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    test_suite='test_flask_marshmallow',
    tests_require=['pytest', 'mock'],
    cmdclass={'test': PyTest}

)
