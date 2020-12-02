# EventLog keys

EventLog key:

```
HKEY_LOCAL_MACHINE\System\CurrentControlSet\Services\EventLog\
```

On Windows NT it can be found in the SYSTEM Registry file.

The EventLog key contains a per EventLog Type sub key, for example for the
System log type:

```
HKEY_LOCAL_MACHINE\System\CurrentControlSet\Services\EventLog\System\
```

Common EventLog type sub key are:

* Application
* Security
* System

The EventLog type sub key contains a per EventLog Source sub key, for example
for the Workstation log source:

```
HKEY_LOCAL_MACHINE\System\CurrentControlSet\Services\EventLog\System\Workstation\
```

Note that the source name is case insensitive; so "Workstation" and
"workstation" are considered equivalent.

## EventLog type sub key

Values:

Value | Data type | Description
--- | --- | ---
Sources | | Array of strings with end-of-string character containing the names of the EventLog sources

## EventLog Source sub key

Values:

Value | Data type | Description
--- | --- | ---
CategoryCount | | Number of event categories supported
CategoryMessageFile | | Path to the category message file. A category message file contains language-dependent strings that describe the categories.
EventMessageFile | | Path to event message files. An event message file contains language-dependent strings that describe the events. Note that this value can contain multiple filenames, for example "C:\WINDOWS\system32\COMRES.DLL;C:\WINDOWS\system32\xpsp2res.dll". Multiple files are delimited using a semicolon.
ParameterMessageFile | | Path to the parameter message file. A parameter message file contains language-independent strings that are to be inserted into the event description strings.
TypesSupported | | Bitmask of supported types

### TypesSupported value data

Value | Identifier | Description
--- | --- | ---
0x0001 | EVENTLOG_ERROR_TYPE |
0x0002 | EVENTLOG_WARNING_TYPE |
0x0004 | EVENTLOG_INFORMATION_TYPE |
0x0008 | EVENTLOG_AUDIT_SUCCESS |
0x0010 | EVENTLOG_AUDIT_FAILURE |

## External Links

* [MSDN: Eventlog Key](https://docs.microsoft.com/en-us/windows/win32/eventlog/eventlog-key)

