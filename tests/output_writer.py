#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the output writer."""

import unittest

from winregrc import output_writers

from tests import test_lib as shared_test_lib


class StdoutOutputWriterTest(shared_test_lib.BaseTestCase):
  """Tests for the stdout output writer."""

  # pylint: disable=protected-access

  def testFormatDataInHexadecimal(self):
    """Tests the _FormatDataInHexadecimal function."""
    test_output_writer = output_writers.StdoutOutputWriter()

    data = b'\x00\x01\x02\x03\x04\x05\x06'
    expected_formatted_data = (
        '0x00000000  00 01 02 03 04 05 06                              '
        '.......\n'
        '\n')
    formatted_data = test_output_writer._FormatDataInHexadecimal(data)
    self.assertEqual(formatted_data, expected_formatted_data)

    data = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09'
    expected_formatted_data = (
        '0x00000000  00 01 02 03 04 05 06 07  08 09                    '
        '..........\n'
        '\n')
    formatted_data = test_output_writer._FormatDataInHexadecimal(data)
    self.assertEqual(formatted_data, expected_formatted_data)

    data = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
    expected_formatted_data = (
        '0x00000000  00 01 02 03 04 05 06 07  08 09 0a 0b 0c 0d 0e 0f  '
        '................\n'
        '\n')
    formatted_data = test_output_writer._FormatDataInHexadecimal(data)
    self.assertEqual(formatted_data, expected_formatted_data)

    data = (
        b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
        b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
        b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f')
    expected_formatted_data = (
        '0x00000000  00 01 02 03 04 05 06 07  08 09 0a 0b 0c 0d 0e 0f  '
        '................\n'
        '...\n'
        '0x00000020  00 01 02 03 04 05 06 07  08 09 0a 0b 0c 0d 0e 0f  '
        '................\n'
        '\n')
    formatted_data = test_output_writer._FormatDataInHexadecimal(data)
    self.assertEqual(formatted_data, expected_formatted_data)

  def testOpenClose(self):
    """Tests the Open and Close functions."""
    test_output_writer = output_writers.StdoutOutputWriter()

    result = test_output_writer.Open()
    self.assertTrue(result)

    test_output_writer.Close()

  def testWriteDebugData(self):
    """Tests the WriteDebugData function."""
    test_output_writer = output_writers.StdoutOutputWriter()

    test_output_writer.WriteDebugData('Description', b'DATA')

  def testWriteValue(self):
    """Tests the WriteValue function."""
    test_output_writer = output_writers.StdoutOutputWriter()

    test_output_writer.WriteValue('Description', 'Value')

  def testWriteText(self):
    """Tests the WriteText function."""
    test_output_writer = output_writers.StdoutOutputWriter()

    test_output_writer.WriteText('Test')


if __name__ == '__main__':
  unittest.main()
