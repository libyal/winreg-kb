# -*- coding: utf-8 -*-
"""Windows Event Log providers collector."""

import logging

from winregrc import interface


class EventLogProvider(object):
  """Windows Event Log provider.

  Attributes:
    category_message_files (list[str]): filenames of the category message files.
    event_message_files (list[str]): filenames of the event message files.
    identifier (str): identifier of the provider, contains a GUID.
    log_sources (list[str]): names of the Windows Event Log source.
    log_type (str): Windows Event Log type.
    parameter_message_files (list[str]): filenames of the parameter message
        files.
  """

  def __init__(
      self, category_message_files, event_message_files, identifier,
      log_source, log_type, parameter_message_files):
    """Initializes a Windows Event Log provider.

    Args:
      category_message_files (list[str]): filenames of the category message
          files.
      event_message_files (list[str]): filenames of the event message files.
      identifier (str): identifier of the provider, contains a GUID.
      log_source (str): name of the Windows Event Log source.
      log_type (str): Windows Event Log type.
      parameter_message_files (list[str]): filenames of the parameter message
          files.
    """
    super(EventLogProvider, self).__init__()
    self.category_message_files = category_message_files
    self.event_message_files = event_message_files
    self.identifier = identifier
    self.log_sources = [log_source]
    self.log_type = log_type
    self.parameter_message_files = parameter_message_files


class EventLogProvidersCollector(interface.WindowsRegistryKeyCollector):
  """Windows Event Log providers collector."""

  _SERVICES_EVENTLOG_KEY_PATH = (
      'HKEY_LOCAL_MACHINE\\System\\CurrentControlSet\\Services\\EventLog')

  _WINEVT_PUBLISHERS_KEY_PATH = (
      'HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows\\CurrentVersion\\'
      'WINEVT\\Publishers')

  def _CollectEventLogProvidersFromPublishersKeys(self, winevt_publishers_key):
    """Retrieves Event Log providers from a WINEVT publishers key.

    Args:
      winevt_publishers_key (dfwinreg.WinRegistryKey): WINEVT publishers key.

    Yield:
      EventLogProvider: Event Log provider.
    """
    if winevt_publishers_key:
      for guid_key in winevt_publishers_key.GetSubkeys():
        log_source = self._GetValueAsStringFromKey(guid_key, '')

        event_message_files = self._GetValueAsStringFromKey(
            guid_key, 'MessageFileName', default_value='')
        event_message_files = sorted(filter(None, [
            path.strip().lower() for path in event_message_files.split(';')]))

        provider_identifier = guid_key.name.lower()

        yield EventLogProvider(
            [], event_message_files, provider_identifier, log_source, '', [])

  def _CollectEventLogProvidersFromRegistry(self, registry):
    """Retrieves Event Log providers from a Windows Registry.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.

    Returns:
      list[EventLogProvider]: Event Log providers.
    """
    services_eventlog_key = registry.GetKeyByPath(
        self._SERVICES_EVENTLOG_KEY_PATH)
    winevt_publishers_key = registry.GetKeyByPath(
        self._WINEVT_PUBLISHERS_KEY_PATH)

    if not services_eventlog_key and not winevt_publishers_key:
      return []

    eventlog_providers_per_identifier = {}
    eventlog_providers_per_log_source = {}

    for eventlog_provider in self._CollectEventLogProvidersFromServicesKey(
        services_eventlog_key):
      log_source = eventlog_provider.log_sources[0]

      existing_eventlog_provider = eventlog_providers_per_identifier.get(
          eventlog_provider.identifier, None)
      if existing_eventlog_provider:
        self._UpdateExistingEventLogProvider(
             existing_eventlog_provider, eventlog_provider)
        continue

      if log_source in eventlog_providers_per_log_source:
        logging.warning((
            'Found multiple definitions for Event Log provider: '
            '{0:s}').format(log_source))
        continue

      eventlog_providers_per_log_source[log_source] = eventlog_provider

      if eventlog_provider.identifier:
        eventlog_providers_per_identifier[eventlog_provider.identifier] = (
              eventlog_provider)

    for eventlog_provider in self._CollectEventLogProvidersFromPublishersKeys(
        winevt_publishers_key):
      log_source = eventlog_provider.log_sources[0]

      existing_eventlog_provider = eventlog_providers_per_log_source.get(
          log_source, None)
      if not existing_eventlog_provider:
        existing_eventlog_provider = eventlog_providers_per_identifier.get(
            eventlog_provider.identifier, None)

        if existing_eventlog_provider:
          if log_source not in existing_eventlog_provider.log_sources:
            existing_eventlog_provider.log_sources.append(log_source)

      if existing_eventlog_provider:
        # TODO: handle mismatches where message files don't define a path.

        if not existing_eventlog_provider.event_message_files:
          existing_eventlog_provider.event_message_files = (
              eventlog_provider.event_message_files)
        elif eventlog_provider.event_message_files not in (
            [], existing_eventlog_provider.event_message_files):
          # TODO: check if one only defines a filename while the other a path.
          # ['%systemroot%\\system32\\winhttp.dll'] != ['winhttp.dll']
          logging.warning((
              'Mismatch in event message files of alternate definition: '
              '{0:s} for Event Log provider: {1:s}').format(
                  log_source, ', '.join(
                      existing_eventlog_provider.log_sources)))

        if not existing_eventlog_provider.identifier:
          existing_eventlog_provider.identifier = eventlog_provider.identifier
        elif existing_eventlog_provider.identifier != (
            eventlog_provider.identifier):
          logging.warning((
              'Mismatch in provider identifier of alternate definition: '
              '{0:s} for Event Log provider: {1:s}').format(
                  log_source, ', '.join(
                      existing_eventlog_provider.log_sources)))

      else:
        eventlog_providers_per_log_source[log_source] = eventlog_provider
        eventlog_providers_per_identifier[eventlog_provider.identifier] = (
            eventlog_provider)

    return [eventlog_provider for _, eventlog_provider in sorted(
        eventlog_providers_per_log_source.items())]

  def _CollectEventLogProvidersFromServicesKey(self, services_eventlog_key):
    """Retrieves Event Log providers from a services Event Log key.

    Args:
      services_eventlog_key (dfwinreg.WinRegistryKey): services Event Log key.

    Yield:
      EventLogProvider: Event Log provider.
    """
    if services_eventlog_key:
      for log_type_key in services_eventlog_key.GetSubkeys():
        for provider_key in log_type_key.GetSubkeys():
          log_source = provider_key.name
          log_type = log_type_key.name

          category_message_files = self._GetValueAsStringFromKey(
              provider_key, 'CategoryMessageFile', default_value='')
          category_message_files = sorted(filter(None, [
              path.strip().lower()
              for path in category_message_files.split(';')]))

          event_message_files = self._GetValueAsStringFromKey(
              provider_key, 'EventMessageFile', default_value='')
          event_message_files = sorted(filter(None, [
              path.strip().lower() for path in event_message_files.split(';')]))

          parameter_message_files = self._GetValueAsStringFromKey(
              provider_key, 'ParameterMessageFile', default_value='')
          parameter_message_files = sorted(filter(None, [
              path.strip().lower()
              for path in parameter_message_files.split(';')]))

          provider_identifier = self._GetValueAsStringFromKey(
              provider_key, 'ProviderGuid')
          if provider_identifier:
            provider_identifier = provider_identifier.lower()

          yield EventLogProvider(
              category_message_files, event_message_files, provider_identifier,
              log_source, log_type, parameter_message_files)

  def _UpdateExistingEventLogProvider(
      self, existing_eventlog_provider, eventlog_provider):
    """Updates an existing Event Log provider.

    Args:
      existing_eventlog_provider (EventLogProvider): existing Event Log
          provider.
      eventlog_provider (EventLogProvider): Event Log provider.
    """
    log_source = eventlog_provider.log_sources[0]
    if log_source not in existing_eventlog_provider.log_sources:
      existing_eventlog_provider.log_sources.append(log_source)

    if not existing_eventlog_provider.category_message_files:
      existing_eventlog_provider.category_message_files = (
          eventlog_provider.category_message_files)
    elif eventlog_provider.category_message_files not in (
        [], existing_eventlog_provider.category_message_files):
      logging.warning((
          'Mismatch in category message files of alternate definition: '
          '{0:s} for Event Log provider: {1:s}').format(
              log_source, ', '.join(existing_eventlog_provider.log_sources)))

    if not existing_eventlog_provider.event_message_files:
      existing_eventlog_provider.event_message_files = (
          eventlog_provider.event_message_files)
    elif eventlog_provider.event_message_files not in (
        [], existing_eventlog_provider.event_message_files):
       # TODO: check if one only defines a filename while the other a path.
       # ['%systemroot%\\system32\\winhttp.dll'] != ['winhttp.dll']
      logging.warning((
          'Mismatch in event message files of alternate definition: '
          '{0:s} for Event Log provider: {1:s}').format(
              log_source, ', '.join(existing_eventlog_provider.log_sources)))

    if not existing_eventlog_provider.parameter_message_files:
      existing_eventlog_provider.parameter_message_files = (
          eventlog_provider.parameter_message_files)
    elif eventlog_provider.parameter_message_files not in (
        [], existing_eventlog_provider.parameter_message_files):
      logging.warning((
          'Mismatch in provider message files of alternate definition: '
          '{0:s} for Event Log provider: {1:s}').format(
              log_source, ', '.join(existing_eventlog_provider.log_sources)))

  def Collect(self, registry, output_writer):
    """Collects the Event Log providers.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.
      output_writer (OutputWriter): output writer.

    Returns:
      bool: True if the Event Log providers key was found, False if not.
    """
    result = False
    for eventlog_provider in self._CollectEventLogProvidersFromRegistry(
        registry):
      output_writer.WriteEventLogProvider(eventlog_provider)
      result = True

    return result
