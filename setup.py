# coding: utf-8
import os
import re

from setuptools import setup, find_packages


with open(
    os.path.join(os.path.dirname(__file__), 'stellar', 'app.py')
) as app_file:
    VERSION = re.compile(
        r".*__version__ = '(.*?)'", re.S
    ).match(app_file.read()).group(1)

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
        'PyYAML>=5.3.1',
        'SQLAlchemy>=1.3.22',
        'humanize>=3.2.0',
        'schema>=0.7.2',
        'click>=7.1.2',
        'SQLAlchemy-Utils>=0.36.8',
        'psutil>=5.8.0',
        'wheel>=0.36.2',
        'psycopg2-binary>=2.8.6'
    ]
)
