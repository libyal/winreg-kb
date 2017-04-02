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

    hexdump.Hexdump(b'\x00\x01\x02\x03\x04\x05\x06')

    hexdump.Hexdump(b'\x00\x01\x02\x03\x04\x05\x06\x07\x08')

    hexdump.Hexdump(
        b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f')

    hexdump.Hexdump(
        b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
        b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
        b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f')


if __name__ == '__main__':
  unittest.main()
