# -*- coding: utf-8 -*-
"""Windows EventLog providers collector."""

from winregrc import interface


class EventLogProvider(object):
  """Windows EventLog provider.

  Attributes:
    category_message_files (list[str]): filenames of the category message files.
    event_message_files (list[str]): filenames of the event message files.
    log_source (str): Windows EventLog source.
    log_type (str): Windows EventLog type.
    parameter_message_files (list[str]): filenames of the parameter message
        files.
  """

  def __init__(
      self, category_message_files, event_message_files, log_source, log_type,
      parameter_message_files):
    """Initializes a Windows EventLog provider.

    Args:
      category_message_files (list[str]): filenames of the category message
          files.
      event_message_files (list[str]): filenames of the event message files.
      log_source (str): Windows EventLog source.
      log_type (str): Windows EventLog type.
      parameter_message_files (list[str]): filenames of the parameter message
          files.
    """
    super(EventLogProvider, self).__init__()
    self.category_message_files = category_message_files
    self.event_message_files = event_message_files
    self.log_source = log_source
    self.log_type = log_type
    self.parameter_message_files = parameter_message_files


class EventLogProvidersCollector(interface.WindowsRegistryKeyCollector):
  """Windows EventLog providers collector."""

  _SERVICES_EVENTLOG_KEY_PATH = (
      'HKEY_LOCAL_MACHINE\\System\\CurrentControlSet\\Services\\EventLog')

  def Collect(self, registry, output_writer):
    """Collects the EventLog providers.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.
      output_writer (OutputWriter): output writer.

    Returns:
      bool: True if the EventLog providers key was found, False if not.
    """
    sevices_eventlog_key = registry.GetKeyByPath(
        self._SERVICES_EVENTLOG_KEY_PATH)
    if not sevices_eventlog_key:
      return False

    for log_type_key in sevices_eventlog_key.GetSubkeys():
      for provider_key in log_type_key.GetSubkeys():
        log_source = provider_key.name
        log_type = log_type_key.name

        category_message_files = self._GetValueAsStringFromKey(
            provider_key, 'CategoryMessageFile', default_value='')
        category_message_files = category_message_files.split(';') or None

        event_message_files = self._GetValueAsStringFromKey(
            provider_key, 'EventMessageFile', default_value='')
        event_message_files = event_message_files.split(';') or None

        parameter_message_files = self._GetValueAsStringFromKey(
            provider_key, 'ParameterMessageFile', default_value='')
        parameter_message_files = parameter_message_files.split(';') or None

        eventlog_provider = EventLogProvider(
            category_message_files, event_message_files, log_source, log_type,
            parameter_message_files)
        output_writer.WriteEventLogProvider(eventlog_provider)

    return True
