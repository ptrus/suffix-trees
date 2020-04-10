from setuptools import setup

setup(
    name='suffix-trees',
    packages=['suffix_trees'],
    version='0.3.0',
    description='Suffix trees, generalized suffix trees and string processing methods',
    author='Peter Us',
    author_email='ptrusr@gmail.com',
    url='https://github.com/ptrus/suffix-trees',
    long_description=open('README.rst').read(),
    package_data={},
    include_package_data=True,
    license='MIT',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
