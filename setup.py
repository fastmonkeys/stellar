# coding: utf-8
import os
import re

from setuptools import setup, find_packages


# https://bitbucket.org/zzzeek/alembic/raw/f38eaad4a80d7e3d893c3044162971971ae0
# 09bf/setup.py
v = open(os.path.join(os.path.dirname(__file__), 'stellar', 'app.py'))
VERSION = re.compile(r".*__version__ = '(.*?)'", re.S).match(v.read()).group(1)
v.close()

with open("README.md") as readme:
    long_description = readme.read()

setup(
    name='stellar',
    description=(
        'stellar is a tool for creating and restoring database snapshots'
    ),
    long_description=long_description,
    version=VERSION,
    url='https://github.com/fastmonkeys/stellar',
    license='BSD',
    author=u'Teemu Kokkonen, Pekka Pöyry',
    author_email='teemu@fastmonkeys.com, pekka@fastmonkeys.com',
    packages=find_packages('.', exclude=['examples*', 'test*']),
    entry_points={
        'console_scripts': [ 'stellar = stellar.command:main' ],
    },
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Topic :: Utilities',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Database',
        'Topic :: Software Development :: Version Control',
    ],
    install_requires = [
        'PyYAML',
        'SQLAlchemy',
        'humanize',
        'pytest',
        'schema',
        'click',
        'SQLAlchemy-Utils',
        'psutil',
    ]
)
