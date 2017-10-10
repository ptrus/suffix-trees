from setuptools import setup

import pypandoc
long_description = pypandoc.convert('README.md', 'rst')

setup(
    name='suffix-trees',
    packages=['suffix_trees'],
    version='0.2.4.2',
    description='Suffix trees, generalized suffix trees and string processing methods',
    author='Peter Us',
    author_email='ptrusr@gmail.com',
    url='https://github.com/ptrus/suffix-trees',
    long_description=long_description,
    package_data={},
    include_package_data=True,
    license='MIT',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.0",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],
)
