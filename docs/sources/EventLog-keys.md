# EventLog keys

## EventLog providers

Information about EventLog providers is stored across multiple keys:

* the Services\EventLog key, which has been around since at least Windows NT 3.5
* the WINEVT\Publishers key, which was introduced in Windows Vista

Note that the combined information of both keys can be needed, for example
the Services\EventLog key:

```
Log source              : WinMgmt
Identifier              : {1edeee53-0afe-4609-b846-d8c0b2075b1f}
Log type                : Application
```

In combination with the corresponding WINEVT\Publishers key:

```
Log source              : Microsoft-Windows-WMI
Identifier              : {1edeee53-0afe-4609-b846-d8c0b2075b1f}
Event message files     : %SystemRoot%\system32\wbem\WinMgmtR.dll
```

Is the following EvenLog provider, that has multiple log sources:

```
Log source              : WinMgmt
                        : Microsoft-Windows-WMI
Identifier              : {1edeee53-0afe-4609-b846-d8c0b2075b1f}
Log type                : Application
Event message files     : %systemroot%\system32\wbem\winmgmtr.dll
```

## Services\EventLog key

The event sources are stored in the Services\EventLog key:

```
HKEY_LOCAL_MACHINE\System\CurrentControlSet\Services\EventLog\
```

On Windows NT it can be found in the SYSTEM Registry file.

The Services\EventLog key contains a per EventLog type sub key, for example
for the "System" EventLog type:

```
HKEY_LOCAL_MACHINE\System\CurrentControlSet\Services\EventLog\System\
```

Common EventLog types are:

* Application
* Security
* System

The EventLog type sub key contains a per EventLog source-per-type sub key,
for example for the "Workstation" EventLog source:

```
HKEY_LOCAL_MACHINE\System\CurrentControlSet\Services\EventLog\System\Workstation\
```

Note that the source name is case insensitive; so "Workstation" and
"workstation" are considered equivalent.

### Services\EventLog type sub key

Values:

Name | Data type | Description
--- | --- | ---
Sources | | Array of strings with end-of-string character containing the names of the event sources

#### Services\EventLog source-per-type sub key

The Services\EventLog source-per-type sub key contains information about
a single event source.

Values:

Name | Data type | Description
--- | --- | ---
CategoryCount | REG_DWORD | Number of event categories supported
CategoryMessageFile | REG_EXPAND_SZ | Path to the category message file. A category message file contains language-dependent strings that describe the categories.
EventMessageFile | REG_EXPAND_SZ | Path to event message files. An event message file contains language-dependent strings that describe the events. Note that this value can contain multiple filenames, for example "C:\WINDOWS\system32\COMRES.DLL;C:\WINDOWS\system32\xpsp2res.dll". Multiple files are delimited using a semicolon.
ParameterMessageFile | REG_EXPAND_SZ | Path to the parameter message file. A parameter message file contains language-independent strings that are to be inserted into the event description strings.
ProviderGuid | REG_SZ | Identifier, in the form "{%GUID%}", of the event provider.
TypesSupported | REG_DWORD | Bitmask of supported types

##### TypesSupported value data

Value | Identifier | Description
--- | --- | ---
0x0001 | EVENTLOG_ERROR_TYPE |
0x0002 | EVENTLOG_WARNING_TYPE |
0x0004 | EVENTLOG_INFORMATION_TYPE |
0x0008 | EVENTLOG_AUDIT_SUCCESS |
0x0010 | EVENTLOG_AUDIT_FAILURE |

## WINEVT\Publishers key

The event publishers (or providers) are stored in the WINEVT\Publishers key:

```
HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\WINEVT\Publishers
```

On Windows Vista or later it can be found in the SOFTWARE Registry file.

The WINEVT\Publishers key contains a GUID type sub key, for example
"{de513a55-c345-438b-9a74-e18cac5c5cc5}":

```
HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\WINEVT\Publishers\%GUID%
```

### WINEVT\Publishers GUID sub key

A WINEVT\Publishers GUID sub key contains information about a single event
publisher.

Values:

Name | Data type | Description
--- | --- | ---
(default) | | name of the event source
MessageFileName | | Path to an event message file. An event message file contains language-dependent strings that describe the events.
ResourceFileName | | Path to an event resource file.

## EventLog provider with multiple provider GUIDs

Seen on Windows 8.0, 8.1, 10, 11 and 2012:

```
Key path: HKEY_LOCAL_MACHINE\System\CurrentControlSet\Services\EventLog\Application\Microsoft-Windows-KdsSvc
Name: Microsoft-Windows-KdsSvc
Last written time: Oct 30, 2015 07:25:12.126588100 UTC

Value: 0 providerGuid
Type: string (REG_SZ)
Data size: 78
Data: {D4BE7726-DC7A-11DF-A6E6-0902DFD72085}

Key path: HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\WINEVT\Publishers\{89203471-d554-47d4-bde4-7552ec219999}
Name: {89203471-d554-47d4-bde4-7552ec219999}
Last written time: Oct 30, 2015 07:25:53.860831900 UTC

Value: 0 (default)
Type: string (REG_SZ)
Data size: 50
Data: Microsoft-Windows-KdsSvc

Value: 1 ResourceFileName
Type: expandable string (REG_EXPAND_SZ)
Data size: 66
Data: %SystemRoot%\system32\KdsCli.dll

Value: 2 MessageFileName
Type: expandable string (REG_EXPAND_SZ)
Data size: 66
Data: %SystemRoot%\system32\KdsCli.dll
```

## External Links

* [Eventlog Key](https://docs.microsoft.com/en-us/windows/win32/eventlog/eventlog-key)
* [Event Sources](https://docs.microsoft.com/en-us/windows/win32/eventlog/event-sources)
* [winevt.h header](https://docs.microsoft.com/en-us/windows/win32/api/winevt)
* [Windows Event Log](https://docs.microsoft.com/en-us/windows/win32/api/_wes)

