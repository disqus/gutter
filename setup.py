#!/usr/bin/env python

import sys
import os
from setuptools import find_packages


try:
    from notsetuptools import setup
except ImportError:
    from setuptools import setup

tests_require = [
    'nose', 'exam', 'mock', 'django', 'redis'
]

if sys.version_info < (3, 3):
    tests_require.append('unittest2')
    tests_require.append('nose-performance')


setup_requires = []
if 'nosetests' in sys.argv[1:]:
    setup_requires.append('nose')

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', __name__)
    INSTALLED_APPS = ('gutter.client',)
    SECRET_KEY = 'secret!'

if 'flake8' in sys.argv[1:]:
    setup_requires.append('flake8')
    setup_requires.append('dont-fudge-up')

setup(
    name='gutter',
    version='0.6.0',
    author='DISQUS',
    author_email='opensource@disqus.com',
    url='http://github.com/disqus/gutter',
    description='Client to gutter feature switches backend',
    packages=find_packages(exclude=["tests"]),
    zip_safe=False,
    install_requires=[
        'durabledict>=0.9.0',
        'jsonpickle',
        'werkzeug',
        'six',
    ],
    setup_requires=setup_requires,
    namespace_packages=['gutter'],
    license='Apache License 2.0',
    tests_require=tests_require,
    extras_require={'test': tests_require},
    test_suite='nose.collector',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
