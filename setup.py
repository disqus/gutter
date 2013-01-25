#!/usr/bin/env python

import sys
import os
from setuptools import find_packages

try:
    from notsetuptools import setup
except ImportError:
    from setuptools import setup


tests_require = [
    'nose', 'exam==0.3.1', 'mock', 'nose-performance', 'django', 'redis', 'unittest2'
]

setup_requires = []
if 'nosetests' in sys.argv[1:]:
    setup_requires.append('nose')

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', __name__)
    INSTALLED_APPS = ('gutter.client',)


setup(
    name='gutter',
    version='0.1.2',
    author='DISQUS',
    author_email='opensource@disqus.com',
    url='http://github.com/disqus/gutter',
    description='Client to gutter feature switches backend',
    packages=find_packages(exclude=["tests"]),
    zip_safe=False,
    install_requires=['durabledict>=0.7.0', 'werkzeug'],
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
