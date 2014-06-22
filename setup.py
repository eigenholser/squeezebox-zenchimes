import os
import sys
from setuptools import setup, find_packages
import zenchimes

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

def read(fname):
    """Read text file. Return content."""
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ''

def requires(fname):
    """Read requirements file. Return list."""
    lines = None
    requirements = []
    try:
        with open(fname) as f:
            lines = f.read().splitlines()
    except IOError:
        return []

    for line in lines:
        if not line.startswith('-r'):
            requirements.append(line)
    return requirements

setup(
    name='zenchimes',
    author='eigenholser',
    author_email='eigenholser@gmail.com',
    url='http://eigenholser.com',
    version=zenchimes.__version__,
    description=read('README.rst'),
    long_description=read('README.rst'),
    license=read('LICENSE'),
    platforms=['OS Independent'],
    keywords='python, squeezebox, zen, chimes',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires('requirements/install.txt'),
    tests_require=requires('requirements/test.txt'),
    test_suite='zenchimes.tests.runtests.runtests',
)
