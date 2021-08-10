from setuptools import setup, find_packages
import pkg_resources
import pathlib

with pathlib.Path('requirements.txt').open() as requirements_txt:
    requirements = [str(requirement) for requirement \
                    in pkg_resources.parse_requirements(requirements_txt)]

setup(
    name='pyhac',
    description='A human action controller running on different platforms',
    license='Apache License 2.0',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=requirements,
    include_package_data=True,
    author='JAQQ',
    author_email='dabit-lucas@gmail.com, chen.jiunhan@gmail.com',
    packages=find_packages(),
    keywords='human action controller',
    url='https://github.com/dabit-lucas/hac'
)
