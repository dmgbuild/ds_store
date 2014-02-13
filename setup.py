# -*- coding: utf-8 -*-
from setuptools import setup

setup(name='ds_store',
      version='1.0.0',
      description='Manipulate Finder .DS_Store files from Python',
      long_description=u"""
``ds_store`` lets you examine and modify ``.DS_Store`` files from Python code;
since it is written in pure Python, it is portable and will run on any
platform, not just Mac OS X.

Credit is due to Wim Lewis <wiml@hhhh.org>, Mark Mentovai and
Yvan Barthélemy for reverse-engineering the .DS_Store file format.
See `Wim Lewis’ excellent documentation on CPAN`__ for more information.

__ http://search.cpan.org/~wiml/Mac-Finder-DSStore/DSStoreFormat.pod
""",
      author='Alastair Houghton',
      author_email='alastair@alastairs-place.net',
      url='http://alastairs-place.net/projects/ds_store',
      license='MIT License',
      platforms='Any',
      packages=['ds_store'],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'License :: OSI Approved :: MIT License',
          'Topic :: Desktop Environment',
          'Topic :: Software Development :: Libraries :: Python Modules'],
      install_requires=[
          'biplist >= 0.6',
          'six >= 1.4.1'
          ],
      provides=[
          'ds_store'
          ])
