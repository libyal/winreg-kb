# -*- coding: utf-8 -*-
"""Shared test case."""

import os
import unittest

from winregrc import output_writers


class BaseTestCase(unittest.TestCase):
  """The base test case."""

  _TEST_DATA_PATH = os.path.join(os.getcwd(), 'test_data')

  # Show full diff results, part of TestCase so does not follow our naming
  # conventions.
  maxDiff = None

  def _GetTestFilePath(self, path_segments):
    """Retrieves the path of a test file in the test data directory.

    Args:
      path_segments (list[str]): path segments inside the test data directory.

    Returns:
      str: path of the test file.
    """
    # Note that we need to pass the individual path segments to os.path.join
    # and not a list.
    return os.path.join(self._TEST_DATA_PATH, *path_segments)

  def _SkipIfPathNotExists(self, path):
    """Skips the test if the path does not exist.

    Args:
      path (str): path of a test file.

    Raises:
      SkipTest: if the path does not exist and the test should be skipped.
    """
    if not os.path.exists(path):
      filename = os.path.basename(path)
      raise unittest.SkipTest('missing test file: {0:s}'.format(filename))


class TestOutputWriter(output_writers.StdoutOutputWriter):
  """Test output writer.

  Attributes:
    output (list[str]): output written.
  """

  def __init__(self):
    """Initializes a test output writer."""""
    super(TestOutputWriter, self).__init__()
    self.output = []

  def Close(self):
    """Closes the output writer object."""
    return

  def Open(self):
    """Opens the output writer object."""
    return

  def WriteText(self, text):
    """Writes text to the output.

    Args:
      text (str): text to write.
    """
    self.output.append(text)
