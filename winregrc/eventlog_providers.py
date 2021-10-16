# -*- coding: utf-8 -*-
"""Windows EventLog providers collector."""

import logging

from winregrc import interface


class EventLogProvider(object):
  """Windows EventLog provider.

  Attributes:
    category_message_files (list[str]): filenames of the category message files.
    event_message_files (list[str]): filenames of the event message files.
    identifier (str): identifier of the provider, contains a GUID.
    log_source (str): name of the Windows EventLog source.
    log_source_alias (str): Alternative name of the Windows EventLog source.
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
      log_source (str): name of the Windows EventLog source.
      log_type (str): Windows EventLog type.
      parameter_message_files (list[str]): filenames of the parameter message
          files.
    """
    super(EventLogProvider, self).__init__()
    self.category_message_files = category_message_files
    self.event_message_files = event_message_files
    self.identifier = identifier
    self.log_source = log_source
    self.log_source_alias = None
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

    eventlog_providers_per_identifier = {}
    eventlog_providers_per_log_source = {}

    if sevices_eventlog_key:
      for log_type_key in sevices_eventlog_key.GetSubkeys():
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

          existing_eventlog_provider = eventlog_providers_per_identifier.get(
              provider_identifier, None)
          if existing_eventlog_provider:
            if existing_eventlog_provider.log_source_alias not in (
                None, log_source):
              logging.warning(
                  'EventLog provider: {0:s} already has an alias'.format(
                      existing_eventlog_provider.log_source))
              continue

            existing_eventlog_provider.log_source_alias = log_source

            if not existing_eventlog_provider.category_message_files:
              existing_eventlog_provider.category_message_files = (
                  category_message_files)
            elif category_message_files not in (
                [], existing_eventlog_provider.category_message_files):
              logging.warning((
                  'Mismatch in category message files of alternate definition: '
                  '{0:s} for EventLog provider: {1:s}').format(
                      log_source, existing_eventlog_provider.log_source))

            if not existing_eventlog_provider.event_message_files:
              existing_eventlog_provider.event_message_files = (
                  event_message_files)
            elif event_message_files not in (
                [], existing_eventlog_provider.event_message_files):
              logging.warning((
                  'Mismatch in event message files of alternate definition: '
                  '{0:s} for EventLog provider: {1:s}').format(
                      log_source, existing_eventlog_provider.log_source))

            if not existing_eventlog_provider.parameter_message_files:
              existing_eventlog_provider.parameter_message_files = (
                  parameter_message_files)
            elif parameter_message_files not in (
                [], existing_eventlog_provider.parameter_message_files):
              logging.warning((
                  'Mismatch in provider message files of alternate definition: '
                  '{0:s} for EventLog provider: {1:s}').format(
                      log_source, existing_eventlog_provider.log_source))

            continue

          eventlog_provider = EventLogProvider(
              category_message_files, event_message_files, provider_identifier,
              log_source, log_type, parameter_message_files)

          if log_source in eventlog_providers_per_log_source:
            logging.warning((
                'Found multiple definitions for EventLog provider: '
                '{0:s}').format(log_source))
            continue

          eventlog_providers_per_log_source[log_source] = eventlog_provider

          if provider_identifier:
            eventlog_providers_per_identifier[provider_identifier] = (
                  eventlog_provider)

    if winevt_publishers_key:
      for guid_key in winevt_publishers_key.GetSubkeys():
        log_source = self._GetValueAsStringFromKey(guid_key, '')

        event_message_files = self._GetValueAsStringFromKey(
            guid_key, 'MessageFileName', default_value='')
        event_message_files = sorted(filter(None, [
            path.strip().lower() for path in event_message_files.split(';')]))

        provider_identifier = guid_key.name.lower()

        existing_eventlog_provider = eventlog_providers_per_log_source.get(
            log_source, None)
        if not existing_eventlog_provider:
          existing_eventlog_provider = eventlog_providers_per_identifier.get(
              provider_identifier, None)

          if existing_eventlog_provider:
            existing_eventlog_provider.log_source_alias = (
                existing_eventlog_provider.log_source)
            existing_eventlog_provider.log_source = log_source

        if existing_eventlog_provider:
          # TODO: handle mismatches where message files don't define a path.

          if not existing_eventlog_provider.event_message_files:
            existing_eventlog_provider.event_message_files = event_message_files
          elif event_message_files not in (
              [], existing_eventlog_provider.event_message_files):
            logging.warning((
                'Mismatch in event message files of alternate definition: '
                '{0:s} for EventLog provider: {1:s}').format(
                    existing_eventlog_provider.log_source_alias,
                    existing_eventlog_provider.log_source))

          if not existing_eventlog_provider.identifier:
            existing_eventlog_provider.identifier = provider_identifier
          elif existing_eventlog_provider.identifier != provider_identifier:
            logging.warning((
                'Mismatch in provider identifier of alternate definition: '
                '{0:s} for EventLog provider: {1:s}').format(
                    existing_eventlog_provider.log_source_alias,
                    existing_eventlog_provider.log_source))

        else:
          eventlog_provider = EventLogProvider(
              [], event_message_files, provider_identifier, log_source, '', [])

          eventlog_providers_per_log_source[log_source] = eventlog_provider
          eventlog_providers_per_identifier[provider_identifier] = (
              eventlog_provider)

    for _, eventlog_provider in sorted(
        eventlog_providers_per_log_source.items()):
      output_writer.WriteEventLogProvider(eventlog_provider)

    return True
