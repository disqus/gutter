#!/usr/bin/env python

import sys
from setuptools import find_packages

try:
    from notsetuptools import setup
except ImportError:
    from setuptools import setup


tests_require = [
    'nose', 'exam'
]

setup_requires = []
if 'nosetests' in sys.argv[1:]:
    setup_requires.append('nose')


setup(
    name='gargoyle-client',
    version='0.1.0',
    author='DISQUS',
    author_email='opensource@disqus.com',
    url='http://github.com/disqus/gargoyle-client',
    description='Client to gargoyle feature switches backend',
    packages=find_packages(exclude=["tests"]),
    zip_safe=False,
    install_requires=['modeldict>=0.1.0'],
    setup_requires=setup_requires,
    namespace_packages=['gargoyle'],
    license='Apache License 2.0',
    tests_require=tests_require,
    extras_require={'test': tests_require},
    test_suite='nose.collector',
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
