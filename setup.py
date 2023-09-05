"""
setup.py - Setup file to distribute the library

See Also:
    https://github.com/pypa/sampleproject
    https://packaging.python.org/en/latest/distributing.html
    https://pythonhosted.org/an_example_pypi_project/setuptools.html
"""
import os
import glob
import sys
from setuptools import setup, Extension, find_packages


def read(fname):
    """Read in a file"""
    with open(os.path.join(os.path.dirname(__file__), fname), 'r') as file:
        return file.read()


if __name__ == "__main__":
    # Variables
    name = "heic_to_jpg"
    version = "0.0.0"
    description = "Convert heic files to jpg and keep metadata"
    url = "https://github.com/justengel/heic_to_jpg"
    author = "Justin Engel"
    author_email = "jtengel08@gmail.com"
    keywords = 'heic jpg'
    packages = find_packages(exclude=('tests', 'docs', 'bin'))

    # Extensions
    extensions = [
        # Extension('libname',
        #           # define_macros=[('MAJOR_VERSION', '1')],
        #           # extra_compile_args=['-std=c99'],
        #           sources=['file.c', 'dir/file.c'],
        #           include_dirs=['./dir'])
        ]

    setup(name=name,
          version=version,
          description=description,
          long_description=read('README.rst'),
          keywords=keywords,
          url=url,
          download_url='{url}/archive/refs/tags/v{version}.tar.gz'.format(url=url, version=version),
          author=author,
          author_email=author_email,

          license='Proprietary',
          platforms='any',
          classifiers=['Programming Language :: Python',
                       'Programming Language :: Python :: 3',
                       'Operating System :: OS Independent'],

          scripts=[file for file in glob.iglob('bin/*.py')],  # Run with python -m Scripts.module args

          ext_modules=extensions,  # C extensions
          packages=packages,
          include_package_data=True,
          package_data={pkg: ['*', '*/*', '*/*/*', '*/*/*/*', '*/*/*/*/*']
                        for pkg in packages if '/' not in pkg and '\\' not in pkg},

          # Data files outside of packages
          # data_files=[('my_data', ['data/my_data.dat'])],

          # options to install extra requirements
          install_requires=[
              "Pillow >= 10.0.0",
              "pillow_heif >= 0.13.0",
              ],
          extras_require={
              },

          entry_points={
              'console_scripts': [
                  'heic_to_jpg=heic_to_jpg:cli',
                  ],
              # 'gui_scripts': [
              #     'baz = my_package_gui:start_func',
              #     ]
              }
          )