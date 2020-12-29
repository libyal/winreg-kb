#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the Python 2 and 3 compatible type definitions."""

import sys
import unittest

# pylint: disable=no-name-in-module,wrong-import-position

if sys.version_info[0] < 3:
  from mock import MagicMock  # pylint: disable=import-error
else:
  from unittest.mock import MagicMock  # pylint: disable=import-error
  from importlib import reload  # pylint: disable=redefined-builtin

from winregrc import py2to3

from tests import test_lib as shared_test_lib


class Py2To3Test(shared_test_lib.BaseTestCase):
  """Tests for the Python 2 and 3 compatible type definitions."""

  _SYS_MODULE = sys

  @unittest.skipIf(sys.version_info[0] > 2, 'Python version not supported')
  def testPython2Definitions(self):
    """Tests the Python 2 definitions."""
    mock_sys = MagicMock(version_info=[2, 7])

    self._SYS_MODULE.modules['sys'] = mock_sys

    reload(py2to3)

    self._SYS_MODULE.modules['sys'] = self._SYS_MODULE

    # Make sure to reload the module after clearing the mock.
    reload(py2to3)

  def testPython3Definitions(self):
    """Tests the Python 3 definitions."""
    mock_sys = MagicMock(version_info=[3, 4])

    self._SYS_MODULE.modules['sys'] = mock_sys

    reload(py2to3)

    self._SYS_MODULE.modules['sys'] = self._SYS_MODULE

    # Make sure to reload the module after clearing the mock.
    reload(py2to3)


if __name__ == '__main__':
  unittest.main()
