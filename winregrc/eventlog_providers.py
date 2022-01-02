# -*- coding: utf-8 -*-
"""Windows Event Log providers collector."""

import logging

from winregrc import interface


class EventLogProvider(object):
  """Windows Event Log provider.

  Attributes:
    additional_identifier (str): additional identifier of the provider,
        contains a GUID.
    category_message_files (set[str]): paths of the category message files.
    event_message_files (set[str]): paths of the event message files.
    identifier (str): identifier of the provider, contains a GUID.
    log_sources (list[str]): names of the Windows Event Log source.
    log_type (str): Windows Event Log type.
    parameter_message_files (set[str]): paths of the parameter message
        files.
  """

  def __init__(self, identifier, log_source, log_type):
    """Initializes a Windows Event Log provider.

    Args:
      identifier (str): identifier of the provider, contains a GUID.
      log_source (str): name of the Windows Event Log source.
      log_type (str): Windows Event Log type.
    """
    super(EventLogProvider, self).__init__()
    self.additional_identifier = None
    self.category_message_files = set()
    self.event_message_files = set()
    self.identifier = identifier
    self.log_sources = [log_source]
    self.log_type = log_type
    self.parameter_message_files = set()


class EventLogProvidersCollector(interface.WindowsRegistryKeyCollector):
  """Windows Event Log providers collector."""

  _SERVICES_EVENTLOG_KEY_PATH = (
      'HKEY_LOCAL_MACHINE\\System\\CurrentControlSet\\Services\\EventLog')

  _WINEVT_PUBLISHERS_KEY_PATH = (
      'HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows\\CurrentVersion\\'
      'WINEVT\\Publishers')

  def _CollectEventLogProviders(
      self, services_eventlog_key, winevt_publishers_key):
    """Collects Windows Event Log providers.

    Args:
      services_eventlog_key (dfwinreg.WinRegistryKey): a Services\\EventLog
          Windows Registry.
      winevt_publishers_key (dfwinreg.WinRegistryKey): a WINEVT\\Publishers
          Windows Registry.

    Yields:
      EventLogProvider: an Event Log provider.
    """
    event_log_providers_per_identifier = {}
    event_log_providers_per_log_source = {}

    for event_log_provider in self._CollectEventLogProvidersFromServicesKey(
        services_eventlog_key):
      log_source = event_log_provider.log_sources[0]

      existing_event_log_provider = event_log_providers_per_identifier.get(
          event_log_provider.identifier, None)
      if existing_event_log_provider:
        if log_source not in existing_event_log_provider.log_sources:
          existing_event_log_provider.log_sources.append(log_source)

        existing_event_log_provider.category_message_files.update(
            event_log_provider.category_message_files)
        existing_event_log_provider.event_message_files.update(
            event_log_provider.event_message_files)
        existing_event_log_provider.parameter_message_files.update(
            event_log_provider.parameter_message_files)

        continue

      if log_source in event_log_providers_per_log_source:
        logging.warning((
            'Found multiple definitions for Event Log provider: '
            '{0:s}').format(log_source))
        continue

      event_log_providers_per_log_source[log_source] = event_log_provider

      if event_log_provider.identifier:
        event_log_providers_per_identifier[event_log_provider.identifier] = (
              event_log_provider)

    for event_log_provider in self._CollectEventLogProvidersFromPublishersKeys(
        winevt_publishers_key):
      log_source = event_log_provider.log_sources[0]

      existing_event_log_provider = event_log_providers_per_log_source.get(
          log_source, None)
      if not existing_event_log_provider:
        existing_event_log_provider = event_log_providers_per_identifier.get(
            event_log_provider.identifier, None)

        if existing_event_log_provider:
          if log_source not in existing_event_log_provider.log_sources:
            existing_event_log_provider.log_sources.append(log_source)

      if existing_event_log_provider:
        existing_event_log_provider.event_message_files.update(
            event_log_provider.event_message_files)

        if not existing_event_log_provider.identifier:
          existing_event_log_provider.identifier = event_log_provider.identifier
        elif existing_event_log_provider.identifier != (
            event_log_provider.identifier):
          existing_event_log_provider.additional_identifier = (
              existing_event_log_provider.identifier)
          existing_event_log_provider.identifier = event_log_provider.identifier

      else:
        event_log_providers_per_log_source[log_source] = event_log_provider
        event_log_providers_per_identifier[event_log_provider.identifier] = (
            event_log_provider)

    for _, event_log_provider in sorted(
        event_log_providers_per_log_source.items()):
      message_files = set()
      paths_lower = set()
      for path in event_log_provider.category_message_files:
        path_lower = path.lower()
        if path_lower not in paths_lower:
          paths_lower.add(path_lower)
          message_files.add(path)

      event_log_provider.category_message_files = message_files

      message_files = set()
      paths_lower = set()
      for path in event_log_provider.event_message_files:
        path_lower = path.lower()
        if path_lower not in paths_lower:
          paths_lower.add(path_lower)
          message_files.add(path)

      event_log_provider.event_message_files = message_files

      message_files = set()
      paths_lower = set()
      for path in event_log_provider.parameter_message_files:
        path_lower = path.lower()
        if path_lower not in paths_lower:
          paths_lower.add(path_lower)
          message_files.add(path)

      event_log_provider.parameter_message_files = message_files

      yield event_log_provider

  def _CollectEventLogProvidersFromPublishersKeys(self, winevt_publishers_key):
    """Collects Windows Event Log providers from a WINEVT publishers key.

    Args:
      winevt_publishers_key (dfwinreg.WinRegistryKey): WINEVT publishers key.

    Yield:
      EventLogProvider: Event Log provider.
    """
    if winevt_publishers_key:
      for guid_key in winevt_publishers_key.GetSubkeys():
        provider_identifier = guid_key.name.lower()
        log_source = self._GetValueFromKey(guid_key, '', default_value='')

        event_log_provider = EventLogProvider(
            provider_identifier, log_source, '')

        event_log_provider.event_message_files = (
            self._GetMessageFilePathsFromKey(guid_key, 'MessageFileName'))

        yield event_log_provider

  def _CollectEventLogProvidersFromServicesKey(self, services_eventlog_key):
    """Collects Windows Event Log providers from a services Event Log key.

    Args:
      services_eventlog_key (dfwinreg.WinRegistryKey): services Event Log key.

    Yield:
      EventLogProvider: Event Log provider.
    """
    if services_eventlog_key:
      for log_type_key in services_eventlog_key.GetSubkeys():
        for provider_key in log_type_key.GetSubkeys():
          provider_identifier = self._GetValueFromKey(
              provider_key, 'ProviderGuid')
          if provider_identifier:
            provider_identifier = provider_identifier.lower()

          log_source = provider_key.name
          log_type = log_type_key.name

          event_log_provider = EventLogProvider(
              provider_identifier, log_source, log_type)

          event_log_provider.category_message_files = (
              self._GetMessageFilePathsFromKey(
                  provider_key, 'CategoryMessageFile'))

          event_log_provider.event_message_files = (
              self._GetMessageFilePathsFromKey(
                  provider_key, 'EventMessageFile'))

          event_log_provider.parameter_message_files = (
              self._GetMessageFilePathsFromKey(
                  provider_key, 'ParameterMessageFile'))

          yield event_log_provider

  def _GetMessageFilePathsFromKey(self, registry_key, value_name):
    """Retrieves a value as a list of message file paths.

    Args:
      registry_key (dfwinreg.WinRegistryKey): Windows Registry key.
      value_name (str): name of the value.

    Returns:
      set[str]: paths of message files.
    """
    message_files = set()

    registry_value = registry_key.GetValueByName(value_name)
    if registry_value:
      value_string = registry_value.GetDataAsObject()
      for path in value_string.split(';'):
        path = path.strip()
        if path:
          message_files.add(path)

    return message_files

  def Collect(self, registry):
    """Collects Windows Event Log providers from a Windows Registry.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.

    Returns:
      generator[EventLogProvider]: Event Log provider generator.
    """
    # TODO: add support to collect Event Log providers from all control sets.

    services_eventlog_key = registry.GetKeyByPath(
        self._SERVICES_EVENTLOG_KEY_PATH)
    winevt_publishers_key = registry.GetKeyByPath(
        self._WINEVT_PUBLISHERS_KEY_PATH)

    return self._CollectEventLogProviders(
        services_eventlog_key, winevt_publishers_key)
