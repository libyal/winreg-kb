#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to update the dependencies in various configuration files."""

import os
import sys

# Change PYTHONPATH to include winregrc.
sys.path.insert(0, u'.')

import winregrc.dependencies  # pylint: disable=wrong-import-position


class RequirementsWriter(object):
  """Class to help write a requirements.txt file."""

  _PATH = u'requirements.txt'

  _FILE_HEADER = [
      u'pip >= 7.0.0',
      u'pytest',
      u'mock']

  def Write(self):
    """Writes a requirements.txt file."""
    file_content = []
    file_content.extend(self._FILE_HEADER)

    for dependency in winregrc.dependencies.GetInstallRequires():
      file_content.append(u'{0:s}'.format(dependency))

    file_content = u'\n'.join(file_content)
    file_content = file_content.encode(u'utf-8')

    with open(self._PATH, 'wb') as file_object:
      file_object.write(file_content)


class SetupCfgWriter(object):
  """Class to help write a setup.cfg file."""

  _PATH = u'setup.cfg'

  _MAINTAINER = (
      u'Joachim Metz <joachim.metz@gmail.com>')

  _FILE_HEADER = [
      u'[sdist]',
      u'template = MANIFEST.in',
      u'manifest = MANIFEST',
      u'',
      u'[sdist_test_data]',
      u'template = MANIFEST.test_data.in',
      u'manifest = MANIFEST.test_data',
      u'',
      u'[bdist_rpm]',
      u'release = 1',
      u'packager = {0:s}'.format(_MAINTAINER),
      u'doc_files = ACKNOWLEDGEMENTS',
      u'            AUTHORS',
      u'            LICENSE',
      u'            README',
      u'build_requires = python-setuptools']

  def Write(self):
    """Writes a setup.cfg file."""
    file_content = []
    file_content.extend(self._FILE_HEADER)

    dependencies = winregrc.dependencies.GetRPMRequires()
    for index, dependency in enumerate(dependencies):
      if index == 0:
        file_content.append(u'requires = {0:s}'.format(dependency))
      else:
        file_content.append(u'           {0:s}'.format(dependency))

    file_content = u'\n'.join(file_content)
    file_content = file_content.encode(u'utf-8')

    with open(self._PATH, 'wb') as file_object:
      file_object.write(file_content)


class TravisBeforeInstallScript(object):
  """Class to help write the Travis-CI install.sh file."""

  _PATH = os.path.join(u'config', u'travis', u'install.sh')

  _FILE_HEADER = [
      u'#!/bin/bash',
      u'#',
      u'# Script to set up Travis-CI test VM.',
      u'',
      (u'COVERALL_DEPENDENCIES="python-coverage python-coveralls '
       u'python-docopt";'),
      u'']

  _FILE_FOOTER = [
      u'',
      u'# Exit on error.',
      u'set -e;',
      u'',
      u'if test `uname -s` = "Darwin";',
      u'then',
      u'\tgit clone https://github.com/log2timeline/l2tdevtools.git;',
      u'',
      u'\tmv l2tdevtools ../;',
      u'\tmkdir dependencies;',
      u'',
      (u'\tPYTHONPATH=../l2tdevtools ../l2tdevtools/tools/update.py '
       u'--download-directory=dependencies --preset=winreg-kb;'),
      u'',
      u'elif test `uname -s` = "Linux";',
      u'then',
      u'\tsudo add-apt-repository ppa:gift/dev -y;',
      u'\tsudo apt-get update -q;',
      (u'\tsudo apt-get install -y ${COVERALL_DEPENDENCIES} '
       u'${PYTHON2_DEPENDENCIES} ${PYTHON2_TEST_DEPENDENCIES} '
       u'${PYTHON3_DEPENDENCIES} ${PYTHON3_TEST_DEPENDENCIES};'),
      u'fi',
      u'']

  def Write(self):
    """Writes a setup.cfg file."""
    file_content = []
    file_content.extend(self._FILE_HEADER)

    dependencies = winregrc.dependencies.GetDPKGDepends(exclude_version=True)
    dependencies = u' '.join(dependencies)
    file_content.append(u'PYTHON2_DEPENDENCIES="{0:s}";'.format(dependencies))

    file_content.append(u'')
    file_content.append(u'PYTHON2_TEST_DEPENDENCIES="python-mock";')

    file_content.append(u'')

    dependencies = winregrc.dependencies.GetDPKGDepends(exclude_version=True)
    dependencies = u' '.join(dependencies)
    dependencies = dependencies.replace(u'python', u'python3')
    file_content.append(u'PYTHON3_DEPENDENCIES="{0:s}";'.format(dependencies))

    file_content.append(u'')
    file_content.append(u'PYTHON3_TEST_DEPENDENCIES="python3-mock";')

    file_content.append(u'')

    file_content.extend(self._FILE_FOOTER)

    file_content = u'\n'.join(file_content)
    file_content = file_content.encode(u'utf-8')

    with open(self._PATH, 'wb') as file_object:
      file_object.write(file_content)


if __name__ == u'__main__':
  writer = RequirementsWriter()
  writer.Write()

  writer = SetupCfgWriter()
  writer.Write()

  writer = TravisBeforeInstallScript()
  writer.Write()
