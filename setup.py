#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Installation and deployment script."""

from __future__ import print_function

import glob
import os
import sys

try:
  from setuptools import find_packages, setup
except ImportError:
  from distutils.core import find_packages, setup

try:
  from distutils.command.bdist_msi import bdist_msi
except ImportError:
  bdist_msi = None

try:
  from distutils.command.bdist_rpm import bdist_rpm
except ImportError:
  bdist_rpm = None

version_tuple = (sys.version_info[0], sys.version_info[1])
if version_tuple < (3, 6):
  print((
      'Unsupported Python version: {0:s}, version 3.6 or higher '
      'required.').format(sys.version))
  sys.exit(1)

# Change PYTHONPATH to include winregrc so that we can get the version.
sys.path.insert(0, '.')

import winregrc  # pylint: disable=wrong-import-position


if not bdist_msi:
  BdistMSICommand = None
else:
  class BdistMSICommand(bdist_msi):
    """Custom handler for the bdist_msi command."""

    # pylint: disable=invalid-name
    def run(self):
      """Builds an MSI."""
      # Command bdist_msi does not support the library version, neither a date
      # as a version but if we suffix it with .1 everything is fine.
      self.distribution.metadata.version += '.1'

      bdist_msi.run(self)


if not bdist_rpm:
  BdistRPMCommand = None
else:
  class BdistRPMCommand(bdist_rpm):
    """Custom handler for the bdist_rpm command."""

    # pylint: disable=invalid-name
    def _make_spec_file(self):
      """Generates the text of an RPM spec file.

      Returns:
        list[str]: lines of the RPM spec file.
      """
      # Note that bdist_rpm can be an old style class.
      if issubclass(BdistRPMCommand, object):
        spec_file = super(BdistRPMCommand, self)._make_spec_file()
      else:
        spec_file = bdist_rpm._make_spec_file(self)

      python_package = 'python3'

      description = []
      requires = ''
      summary = ''
      in_description = False

      python_spec_file = []
      for line in iter(spec_file):
        if line.startswith('Summary: '):
          summary = line[9:]

        elif line.startswith('BuildRequires: '):
          line = 'BuildRequires: {0:s}-setuptools, {0:s}-devel'.format(
              python_package)

        elif line.startswith('Requires: '):
          requires = line[10:]
          continue

        elif line.startswith('%description'):
          in_description = True

        elif line.startswith('python setup.py build'):
          if python_package == 'python3':
            line = '%py3_build'
          else:
            line = '%py2_build'

        elif line.startswith('python setup.py install'):
          if python_package == 'python3':
            line = '%py3_install'
          else:
            line = '%py2_install'

        elif line.startswith('%files'):
          lines = [
              '%files -n {0:s}-%{{name}}'.format(python_package),
              '%defattr(644,root,root,755)',
              '%license LICENSE',
              '%doc ACKNOWLEDGEMENTS AUTHORS README']

          lines.extend([
              '%{python3_sitelib}/winregrc/*.py',
              '%{python3_sitelib}/winregrc/*.yaml',
              '%{python3_sitelib}/winregrc*.egg-info/*',
              '',
              '%exclude %{_prefix}/share/doc/*',
              '%exclude %{python3_sitelib}/winregrc/__pycache__/*',
              '%exclude %{_bindir}/*.py'])

          python_spec_file.extend(lines)
          break

        elif line.startswith('%prep'):
          in_description = False

          python_spec_file.append(
              '%package -n {0:s}-%{{name}}'.format(python_package))
          python_summary = 'Python 3 module of {0:s}'.format(summary)

          if requires:
            python_spec_file.append('Requires: {0:s}'.format(requires))

          python_spec_file.extend([
              'Summary: {0:s}'.format(python_summary),
              '',
              '%description -n {0:s}-%{{name}}'.format(python_package)])

          python_spec_file.extend(description)

        elif in_description:
          # Ignore leading white lines in the description.
          if not description and not line:
            continue

          description.append(line)

        python_spec_file.append(line)

      return python_spec_file


winregrc_description = (
    'Windows Registry resources (winregrc)')

winregrc_long_description = (
    'winregrc is a Python module part of winreg-kb to allow reuse of Windows '
    'Registry resources.')

setup(
    name='winregrc',
    version=winregrc.__version__,
    description=winregrc_description,
    long_description=winregrc_long_description,
    license='Apache License, Version 2.0',
    url='https://github.com/libyal/winreg-kb',
    maintainer='Joachim Metz',
    maintainer_email='joachim.metz@gmail.com',
    cmdclass={
        'bdist_msi': BdistMSICommand,
        'bdist_rpm': BdistRPMCommand},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    packages=find_packages('.', exclude=[
        'scripts', 'tests', 'tests.*', 'utils']),
    package_dir={
        'winregrc': 'winregrc'
    },
    include_package_data=True,
    package_data={
        'winregrc': ['*.yaml']
    },
    zip_safe=False,
    scripts=glob.glob(os.path.join('scripts', '[a-z]*.py')),
    data_files=[
        ('share/doc/winregrc', [
            'ACKNOWLEDGEMENTS', 'AUTHORS', 'LICENSE', 'README']),
    ],
)
