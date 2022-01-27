# -*- coding: utf-8 -*-
"""Windows Event Log providers collector."""

from winregrc import interface


class EventLogProvider(object):
  """Windows Event Log provider.

  Attributes:
    additional_identifier (str): additional identifier of the provider,
        contains a GUID.
    category_message_files (set[str]): paths of the category message files.
    event_message_files (set[str]): paths of the event message files.
    identifier (str): identifier of the provider, contains a GUID.
    log_sources (list[str]): names of the corresponding Event Log sources.
    log_types (list[str]): Windows Event Log types.
    name (str): name of the provider.
    parameter_message_files (set[str]): paths of the parameter message
        files.
  """

  def __init__(self):
    """Initializes a Windows Event Log provider."""
    super(EventLogProvider, self).__init__()
    self.additional_identifier = None
    self.category_message_files = set()
    self.event_message_files = set()
    self.identifier = None
    self.log_sources = []
    self.log_types = []
    self.name = None
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
    event_log_providers_per_name = {}

    for event_log_provider in self._CollectEventLogProvidersFromPublishersKeys(
        winevt_publishers_key):
      provider_identifier = event_log_provider.identifier

      existing_event_log_provider = event_log_providers_per_identifier.get(
          provider_identifier, None)
      if existing_event_log_provider:
        self._MergeEventLogProviders(
            existing_event_log_provider, event_log_provider)

      else:
        event_log_providers_per_identifier[provider_identifier] = (
            event_log_provider)

        if event_log_provider.name:
          event_log_providers_per_name[event_log_provider.name] = (
              event_log_provider)

    event_log_providers_per_log_source = {}

    for event_log_provider in self._CollectEventLogProvidersFromServicesKey(
        services_eventlog_key):
      provider_identifier = event_log_provider.identifier

      if provider_identifier:
        existing_event_log_provider = event_log_providers_per_identifier.get(
            provider_identifier, None)
        if existing_event_log_provider:
          self._MergeEventLogProviders(
              existing_event_log_provider, event_log_provider)
          continue

      log_source = event_log_provider.log_sources[0]
      existing_event_log_provider = event_log_providers_per_name.get(
          log_source, None)
      if existing_event_log_provider:
        if (provider_identifier and
            provider_identifier != existing_event_log_provider.identifier):
          existing_event_log_provider.additional_identifier = (
              provider_identifier)

        self._MergeEventLogProviders(
            existing_event_log_provider, event_log_provider)
        continue

      event_log_providers_per_log_source[log_source] = event_log_provider

    event_log_providers = list(event_log_providers_per_identifier.values())
    event_log_providers.extend(event_log_providers_per_log_source.values())

    for event_log_provider in sorted(
        event_log_providers, key=self._GetEventLogProviderSortedKey):
      event_log_provider.category_message_files = self._NormalizeMessageFiles(
          event_log_provider.category_message_files)
      event_log_provider.event_message_files = self._NormalizeMessageFiles(
          event_log_provider.event_message_files)
      event_log_provider.parameter_message_files = self._NormalizeMessageFiles(
          event_log_provider.parameter_message_files)

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
        event_log_provider = EventLogProvider()
        event_log_provider.identifier = guid_key.name.lower()
        event_log_provider.name = self._GetValueFromKey(guid_key, '')

        event_message_files = self._GetMessageFilePathsFromKey(
            guid_key, 'MessageFileName')
        event_log_provider.event_message_files = event_message_files

        # TODO: add support for ResourceFileName value
        # TODO: add support for ParameterFileName value

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
              provider_key, 'ProviderGuid', default_value='')
          provider_identifier = provider_identifier.lower()

          event_log_provider = EventLogProvider()
          event_log_provider.identifier = provider_identifier or None
          event_log_provider.log_sources = [provider_key.name]
          event_log_provider.log_types = [log_type_key.name]

          category_message_files = self._GetMessageFilePathsFromKey(
              provider_key, 'CategoryMessageFile')
          event_log_provider.category_message_files = category_message_files

          event_message_files = self._GetMessageFilePathsFromKey(
              provider_key, 'EventMessageFile')
          event_log_provider.event_message_files = event_message_files

          parameter_message_files = self._GetMessageFilePathsFromKey(
              provider_key, 'ParameterMessageFile')
          event_log_provider.parameter_message_files = parameter_message_files

          yield event_log_provider

  def _GetEventLogProviderSortedKey(self, event_log_provider):
    """Retrieves a key to sort Event Log providers on.

    Args:
      event_log_provider (EventLogProvider): Event Log provider.

    Returns:
      str: key to sort Event Log providers on.
    """
    if not event_log_provider.log_sources:
      return event_log_provider.name or ''

    return event_log_provider.log_sources[0]

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

  def _MergeEventLogProviders(
      self, first_event_log_provider, second_event_log_provider):
    """Merges the information of the second Event Log provider into the first.

    Args:
      first_event_log_provider (EventLogProvider): first Event Log provider.
      second_event_log_provider (EventLogProvider): second Event Log provider.
    """
    for log_source in second_event_log_provider.log_sources:
      if log_source not in first_event_log_provider.log_sources:
        first_event_log_provider.log_sources.append(log_source)

    for log_type in second_event_log_provider.log_types:
      if log_type not in first_event_log_provider.log_types:
        first_event_log_provider.log_types.append(log_type)

    first_event_log_provider.category_message_files.update(
        second_event_log_provider.category_message_files)
    first_event_log_provider.event_message_files.update(
        second_event_log_provider.event_message_files)
    first_event_log_provider.parameter_message_files.update(
        second_event_log_provider.parameter_message_files)

  def _NormalizeMessageFiles(self, message_files):
    """Normalizes the message files.

    Args:
      message_files (list[str]): paths of the message files.

    Returns:
      set[str]: normalized paths of the message files.
    """
    normalized_message_files = set()
    paths_lower = set()
    for path in message_files:
      path_lower = path.lower()
      if path_lower not in paths_lower:
        paths_lower.add(path_lower)
        normalized_message_files.add(path)

    return normalized_message_files

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
