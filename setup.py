import glob
from setuptools import setup, find_packages
import pkg_resources
import pathlib

with pathlib.Path('requirements.txt').open() as requirements_txt:
    requirements = [str(requirement) for requirement \
                    in pkg_resources.parse_requirements(requirements_txt)]

setup(
    name='hac',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=requirements,
    packages=find_packages(),
    include_package_data=True
)
