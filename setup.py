#!/usr/bin/python3
from setuptools import setup, find_packages

setup(name='GammaSpy',
      version='0.0.1',
      description='Post processing utilities for gamma spectroscopy data.',
      author='William Gurecky',
      packages=find_packages(),
      test_suite="tests",
      install_requires=['numpy>=1.8.0', 'h5py>=2.2.0', 'scipy>=0.19', 'numdifftools', 'setuptools', 'xylib-py', 'pyqtgraph'],
      package_data={'': ['*.txt']},
      license='GPLv3',
      author_email='william.gurecky@utexas.edu',
      entry_points={
          'console_scripts': [
              'gammaspy = gammaspy.gamma_gui:main',
          ]
      }
)
