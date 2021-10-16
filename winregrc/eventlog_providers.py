# -*- coding: utf-8 -*-
"""Windows EventLog providers collector."""

from winregrc import interface


class EventLogProvider(object):
  """Windows EventLog provider.

  Attributes:
    category_message_files (list[str]): filenames of the category message files.
    event_message_files (list[str]): filenames of the event message files.
    identifier (str): identifier of the provider, contains a GUID.
    log_source (str): Windows EventLog source.
    log_type (str): Windows EventLog type.
    parameter_message_files (list[str]): filenames of the parameter message
        files.
  """

  def __init__(
      self, category_message_files, event_message_files, identifier,
      log_source, log_type, parameter_message_files):
    """Initializes a Windows EventLog provider.

    Args:
      category_message_files (list[str]): filenames of the category message
          files.
      event_message_files (list[str]): filenames of the event message files.
      identifier (str): identifier of the provider, contains a GUID.
      log_source (str): Windows EventLog source.
      log_type (str): Windows EventLog type.
      parameter_message_files (list[str]): filenames of the parameter message
          files.
    """
    super(EventLogProvider, self).__init__()
    self.category_message_files = category_message_files
    self.event_message_files = event_message_files
    self.identifier = identifier
    self.log_source = log_source
    self.log_type = log_type
    self.parameter_message_files = parameter_message_files


class EventLogProvidersCollector(interface.WindowsRegistryKeyCollector):
  """Windows EventLog providers collector."""

  _SERVICES_EVENTLOG_KEY_PATH = (
      'HKEY_LOCAL_MACHINE\\System\\CurrentControlSet\\Services\\EventLog')

  _WINEVT_PUBLISHERS_KEY_PATH = (
      'HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows\\CurrentVersion\\'
      'WINEVT\\Publishers')

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
    winevt_publishers_key = registry.GetKeyByPath(
        self._WINEVT_PUBLISHERS_KEY_PATH)

    if not sevices_eventlog_key and not winevt_publishers_key:
      return False

    if sevices_eventlog_key:
      for log_type_key in sevices_eventlog_key.GetSubkeys():
        for provider_key in log_type_key.GetSubkeys():
          log_source = provider_key.name
          log_type = log_type_key.name

          category_message_files = self._GetValueAsStringFromKey(
              provider_key, 'CategoryMessageFile', default_value='')
          category_message_files = category_message_files.split(';')

          event_message_files = self._GetValueAsStringFromKey(
              provider_key, 'EventMessageFile', default_value='')
          event_message_files = event_message_files.split(';')

          parameter_message_files = self._GetValueAsStringFromKey(
              provider_key, 'ParameterMessageFile', default_value='')
          parameter_message_files = parameter_message_files.split(';')

          eventlog_provider = EventLogProvider(
              category_message_files, event_message_files, None,
              log_source, log_type, parameter_message_files)
          output_writer.WriteEventLogProvider(eventlog_provider)

    if winevt_publishers_key:
      for guid_key in winevt_publishers_key.GetSubkeys():
        log_source = self._GetValueAsStringFromKey(guid_key, '')

        event_message_files = self._GetValueAsStringFromKey(
            guid_key, 'MessageFileName', default_value='')
        event_message_files = event_message_files.split(';')

        provider_identifier = guid_key.name.lower()

        eventlog_provider = EventLogProvider(
            [], event_message_files, provider_identifier, log_source, '', [])
        output_writer.WriteEventLogProvider(eventlog_provider)

    return True
