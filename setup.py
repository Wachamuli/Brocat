from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup (
    name='brocat',
    packages='brocat',
    include_package_data=True,
    install_requires = requirements,
)