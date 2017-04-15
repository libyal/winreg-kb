# -*- coding: utf-8 -*-
"""Classes to implement an output writer."""

from __future__ import print_function

import abc

from winregrc import hexdump


class OutputWriter(object):
  """Output writer interface."""

  @abc.abstractmethod
  def Close(self):
    """Closes the output writer."""

  @abc.abstractmethod
  def Open(self):
    """Opens the output writer.

    Returns:
      bool: True if successful or False if not.
    """

  @abc.abstractmethod
  def WriteDebugData(self, description, data):
    """Writes data for debugging.

    Args:
      description (str): description to write.
      data (bytes): data to write.
    """

  @abc.abstractmethod
  def WriteIntegerValueAsDecimal(self, description, value):
    """Writes an integer value as decimal for debugging.

    Args:
      description (str): description to write.
      value (int): value to write.
    """

  @abc.abstractmethod
  def WriteValue(self, description, value):
    """Writes a value for debugging.

    Args:
      description (str): description to write.
      value (str): value to write.
    """

  @abc.abstractmethod
  def WriteText(self, text):
    """Writes text for debugging.

    Args:
      text (str): text to write.
    """


class StdoutOutputWriter(OutputWriter):
  """Stdout output writer."""

  def Close(self):
    """Closes the output writer."""
    pass

  def Open(self):
    """Opens the output writer.

    Returns:
      bool: True if successful or False if not.
    """
    return True

  def WriteDebugData(self, description, data):
    """Writes data for debugging.

    Args:
      description (str): description to write.
      data (bytes): data to write.
    """
    self.WriteText(description)

    hexdump_text = hexdump.Hexdump(data)
    self.WriteText(hexdump_text)

  def WriteIntegerValueAsDecimal(self, description, value):
    """Writes an integer value as decimal for debugging.

    Args:
      description (str): description to write.
      value (int): value to write.
    """
    value_string = u'{0:d}'.format(value)
    self.WriteValue(description, value_string)

  def WriteValue(self, description, value):
    """Writes a value for debugging.

    Args:
      description (str): description to write.
      value (object): value to write.
    """
    alignment = 8 - (len(description) / 8) + 1
    text = u'{0:s}{1:s}: {2!s}'.format(description, u'\t' * alignment, value)
    self.WriteText(text)

  def WriteText(self, text):
    """Writes text for debugging.

    Args:
      text (str): text to write.
    """
    print(text.encode(u'utf8'))
