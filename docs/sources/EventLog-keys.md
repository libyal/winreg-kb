# EventLog keys

## EventLog providers

Information about EventLog providers is stored across multiple keys:

* the Services\EventLog key, which has been around since at least Windows NT 3.5
* the WINEVT\Publishers key, which was introduced in Windows Vista

Note that the combined information of both keys can be needed, for example
the Services\EventLog key:

```
Log type                : System
Log source              : Microsoft-Windows-Time-Service
Identifier              : {06edcfeb-0fd0-4e53-acca-a6f8bbf81bcb}
Event message files     : %SystemRoot%\system32\w32time.dll
```

```
Log type                : System
Log source              : W32Time
Identifier              : {06edcfeb-0fd0-4e53-acca-a6f8bbf81bcb}
Event message files     : %SystemRoot%\system32\w32time.dll
```

In combination with the corresponding WINEVT\Publishers key:

```
Name			: Microsoft-Windows-Time-Service
Identifier              : {06edcfeb-0fd0-4e53-acca-a6f8bbf81bcb}
Event message files     : %SystemRoot%\system32\w32time.dll
```

Is the following EvenLog provider:

```
Name			: Microsoft-Windows-Time-Service
Identifier              : {06edcfeb-0fd0-4e53-acca-a6f8bbf81bcb}
Log type                : System
Log source(s)           : Microsoft-Windows-Time-Service
                        : W32Time
Event message files     : %SystemRoot%\system32\w32time.dll
```

Note that an EventLog provider can have multiple log types and log sources.
It is not known if a log source that matches the EventLog provider name can be
deduplicated.

Or as specified as Event XML:

```
<Provider Name='Microsoft-Windows-Time-Service'
          Guid='{06edcfeb-0fd0-4e53-acca-a6f8bbf81bcb}'
          EventSourceName='W32Time'/>
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

Note that the log source is case insensitive; so "Workstation" and "workstation"
are considered equivalent.

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
(default) | REG_SZ | Case insensitive log source.
MessageFileName | REG_EXPAND_SZ | Path to an event message file. An event message file contains language-dependent strings that describe the events.
ResourceFileName | REG_EXPAND_SZ | Path to an event resource file.
ParameterFileName | REG_EXPAND_SZ | Path to an event parameter file.

## Message file paths

A message file path can be defined in numerous different ways for example:

As an absolute path

```
C:\Windows\System32\mscoree.dll
```

As a relative path:

```
mscoree.dll
```

As a path using environment variables:

```
%SystemDrive%\Windows\System32\mscoree.dll
%SystemRoot%\System32\mscoree.dll
%WinDir%\System32\mscoree.dll
```

As a path using universal OEM runtime macros:

```
$(runtime.system32)\mscoree.dll
```

```
\SystemRoot\system32\mscoree.dll
```

## EventLog provider with multiple provider GUIDs

Seen on Windows 8.0, 8.1, 10, 11 and 2012:

```
Key path: HKEY_LOCAL_MACHINE\System\CurrentControlSet\Services\EventLog\Application\Microsoft-Windows-KdsSvc
Name: Microsoft-Windows-KdsSvc
Last written time: Oct 30, 2015 07:25:12.126588100 UTC

Value: 0 providerGuid
Type: string (REG_SZ)
Data size: 78
Data: {d4be7726-dc7a-11df-a6e6-0902dfd72085}
```

```
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

## EventLog provider with multiple log types

Seen on Windows 10:

```
Key path: HKEY_LOCAL_MACHINE\System\CurrentControlSet\Services\EventLog\Application\Microsoft-Windows-EventCollector
Name: Microsoft-Windows-EventCollector
Last written time: Sep 13, 2014 07:27:56.080450600 UTC

Value: 0 ProviderGuid
Type: string (REG_SZ)
Data size: 78
Data: {b977cf02-76f6-df84-cc1a-6a4b232322b6}

Value: 1 EventMessageFile
Type: expandable string (REG_EXPAND_SZ)
Data size: 66
Data: %SystemRoot%\system32\wecsvc.dll
```

```
Key path: HKEY_LOCAL_MACHINE\System\CurrentControlSet\Services\EventLog\System\Microsoft-Windows-EventCollector
Name: Microsoft-Windows-EventCollector
Last written time: Sep 13, 2014 07:27:56.080450600 UTC

Value: 0 ProviderGuid
Type: string (REG_SZ)
Data size: 78
Data: {b977cf02-76f6-df84-cc1a-6a4b232322b6}

Value: 1 EventMessageFile
Type: expandable string (REG_EXPAND_SZ)
Data size: 66
Data: %SystemRoot%\system32\wecsvc.dll
```

```
Key path:  HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\WINEVT\Publishers\{b977cf02-76f6-df84-cc1a-6a4b232322b6}
Name: {b977cf02-76f6-df84-cc1a-6a4b232322b6}
Last written time: Sep 13, 2014 07:27:56.080450600 UTC

Value: 0 (default)
Type: string (REG_SZ)
Data size: 66
Data: Microsoft-Windows-EventCollector

Value: 1 ResourceFileName
Type: expandable string (REG_EXPAND_SZ)
Data size: 66
Data: %SystemRoot%\system32\wecsvc.dll

Value: 2 MessageFileName
Type: expandable string (REG_EXPAND_SZ)
Data size: 66
Data: %SystemRoot%\system32\wecsvc.dll
```

## External Links

* [Eventlog Key](https://docs.microsoft.com/en-us/windows/win32/eventlog/eventlog-key)
* [Event Sources](https://docs.microsoft.com/en-us/windows/win32/eventlog/event-sources)
* [winevt.h header](https://docs.microsoft.com/en-us/windows/win32/api/winevt)
* [Windows Event Log](https://docs.microsoft.com/en-us/windows/win32/api/_wes)

