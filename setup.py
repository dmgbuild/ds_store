# -*- coding: utf-8 -*-
import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

with open('README.rst', 'rb') as f:
    longdesc = f.read().decode('utf-8')

setup(name='ds_store',
      version='1.2.0',
      description='Manipulate Finder .DS_Store files from Python',
      long_description=longdesc,
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
          'mac_alias >= 2.0.1',
          ],
      tests_require=['pytest'],
      scripts=['scripts/ds_store'],
      cmdclass={
          'test': PyTest
          },
      provides=[
          'ds_store'
          ])
