# EventLog keys

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

Value | Data type | Description
--- | --- | ---
Sources | | Array of strings with end-of-string character containing the names of the event sources

#### Services\EventLog source-per-type sub key

The Services\EventLog source-per-type sub key contains information about
a single event source.

Values:

Value | Data type | Description
--- | --- | ---
CategoryCount | | Number of event categories supported
CategoryMessageFile | | Path to the category message file. A category message file contains language-dependent strings that describe the categories.
EventMessageFile | | Path to event message files. An event message file contains language-dependent strings that describe the events. Note that this value can contain multiple filenames, for example "C:\WINDOWS\system32\COMRES.DLL;C:\WINDOWS\system32\xpsp2res.dll". Multiple files are delimited using a semicolon.
ParameterMessageFile | | Path to the parameter message file. A parameter message file contains language-independent strings that are to be inserted into the event description strings.
TypesSupported | | Bitmask of supported types

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

Value | Data type | Description
--- | --- | ---
(default) | | name of the event source
MessageFileName | | Path to an event message file. An event message file contains language-dependent strings that describe the events.
ResourceFileName | | Path to an event resource file.

## External Links

* [Eventlog Key](https://docs.microsoft.com/en-us/windows/win32/eventlog/eventlog-key)
* [Event Sources](https://docs.microsoft.com/en-us/windows/win32/eventlog/event-sources)
* [winevt.h header](https://docs.microsoft.com/en-us/windows/win32/api/winevt)
* [Windows Event Log](https://docs.microsoft.com/en-us/windows/win32/api/_wes)

