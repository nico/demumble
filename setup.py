#!/usr/bin/env python

import setuptools

setuptools.setup(name='demumble',
      version='1.2.17',
      description='Demangle C++ names',
      url='www.example.com',
      author='nico, stevemk14ebr',
      packages=setuptools.find_packages(),
      package_data={'': ['libdemumble_shared.so', 'demumble_shared.dll']},
      include_package_data=True,
     )
