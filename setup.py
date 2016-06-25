from codecs import open
from os.path import abspath, dirname, join

from setuptools import find_packages, setup

from obs import __version__


this_dir = abspath(dirname(__file__))
with open(join(this_dir, 'README.rst'), encoding='utf-8') as file:
    long_description = file.read()

setup(
    name = 'obs',
    version = __version__,
    description = 'A extensible service for relaying mq events to and from services, e.g., Hangouts',
    long_description = long_description,
    url = 'https://github.com/nerdfarm/obs',
    author = 'Peter Hong',
    author_email = 'psehong@gmail.com',
    license = 'MIT',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords = 'obs mqtt hangouts',
    packages = find_packages(exclude=['docs', 'test*']),
    install_requires = ['paho-mqtt', 'hangups', 'pyyaml'],
    test_suite = 'nose.collector',
    tests_require = ['nose'],
    extras_require = {
        'test': ['coverage', 'pytest', 'pytest-cov'],
    },
    entry_points = {
        'console_scripts': [
            'obs = obs.__main__:main',
        ],
    }
)
