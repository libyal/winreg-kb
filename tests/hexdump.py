#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the hexadecimal representation functions."""

import unittest

from winregrc import hexdump

from tests import test_lib as shared_test_lib


class HexdumpTest(shared_test_lib.BaseTestCase):
  """Tests for the hexadecimal representation functions."""

  def testHexdump(self):
    """Tests the Collect function."""
    hexdump.Hexdump(b'')

    # TODO: add more tests.


if __name__ == '__main__':
  unittest.main()
