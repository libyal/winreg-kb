# Time zones

## Time zone information key

The time zone information is stored in the following key:

```
HKEY_LOCAL_MACHINE\CurrentControlSet\Control\TimeZoneInformation
```

Values:

Name | Data type | Description
--- | --- | ---
ActiveTimeBias | REG_DWORD | The active time bias, in minutes, as configured for the time zone accounting for daylight saving. This is the bias that was used to configure the CMOS clock.
Bias | REG_DWORD | The current bias, in minutes, for local time translation on this computer.
DaylightBias | REG_DWORD | The bias value, in minutes, to be used during local time translations that occur during daylight saving time.
DaylightName | REG_SZ | A description for daylight saving time.
DaylightStart | REG_BINARY | The date and local time when the transition from standard time to daylight saving time occurs on this operating system. <br/> Contains a SYSTEMTIME structure.
DynamicDaylightTimeDisabled | REG_DWORD | Indicates whether dynamic daylight saving time is disabled. <br/> 0 indicates automatic adjustment <br/> 1 indicates automatic adjustment is disabled
RealTimeIsUniversal | REG_DWORD | Indicates if the CMOS clock is configured by using the local date/time (default) or UTC. <br/> 0 indicates that the CMOS clock is configured for local date/time <br/> 1 indicates that the CMOS clock is configured by using UTC
StandardBias | REG_DWORD | The bias value, in minutes, to be used during local time translations that occur during standard time.
StandardName | REG_SZ | A description for standard time.
StandardStart | REG_BINARY | The date and local time when the transition from daylight saving time to standard time occurs on this operating system. <br/> Contains a SYSTEMTIME structure.
TimeZoneKeyName | REG_SZ | The name of the Time Zones name sub key.

Notes:

* the relation between the local time and bias is as following:

```
UTC = local time + bias
```

* the names are stored outside the Windows Registry and are references using [MUI Form](https://winreg-kb.readthedocs.io/en/latest/sources/windows-registry/MUI-form.html)
for example:

```
@tzres.dll,-931
```

* the TimeZoneKeyName is not always present
* The RealTimeIsUniversal value is not installed in the system by default and is not officially supported by Windows

The values in this key corresponds with the [TIME_ZONE_INFORMATION](https://docs.microsoft.com/en-us/windows/win32/api/timezoneapi/ns-timezoneapi-time_zone_information)
and [DYNAMIC_TIME_ZONE_INFORMATION](https://docs.microsoft.com/en-us/windows/win32/api/timezoneapi/ns-timezoneapi-dynamic_time_zone_information)
structures.

## Time Zones key

The time zones definitions are stored in the following key:

```
HKEY_LOCAL_MACHINE\Software\Microsoft\Windows NT\CurrentVersion\Time Zones
```

Sub keys:

Name | Description
--- | ---
%TIMEZONENAME% |

%TIMEZONENAME% represents the name of the Windows name of the time zone. The
Unicode organization maintains windowsZones.xml to map the Windows names to
corresponding IANA names.

Values:

Name | Data type | Description
--- | --- | ---
TzVersion | REG_DWORD |

### Time Zones %TIMEZONENAME% sub key

Sub keys:

Name | Description
--- | ---
Dynamic DST | Contains the dynamic daylight saving time values

Note that not every Time Zones name sub key contains a Dynamic Daylight Saving
Time sub key (Dynamic DST).

Values:

Name | Data type | Description
--- | --- | ---
Display | REG_SZ | The display name
Dlt | REG_SZ | The description for daylight time
Index | |
MapID | |
MUI_Display | REG_SZ | The display name in [MUI Form](https://winreg-kb.readthedocs.io/en/latest/sources/windows-registry/MUI-form.html)
MUI_Dlt | REG_SZ | The description for daylight time in [MUI Form](https://winreg-kb.readthedocs.io/en/latest/sources/windows-registry/MUI-form.html)
MUI_Std | REG_SZ | The description for standard time in [MUI Form](https://winreg-kb.readthedocs.io/en/latest/sources/windows-registry/MUI-form.html)
Std | REG_SZ | The description for standard time
TZI | REG_BINARY | Time zone information <br/> Contains a Registry Time Zone information structure

#### Dynamic Daylight Saving Time sub key

The Dynamic Daylight Saving Time sub key contains time zone information for time zones that apply different daylight saving per year.

Values:

Name | Data type | Description
--- | --- | ---
FirstEntry | REG_DWORD | The first year in the key
LastEntry | REG_DWORD | The last year in the key
%YEAR% | REG_BINARY | Time zone information <br/> Contains a Registry Time Zone information structure

Where %YEAR% represents the year the dynamic daylight saving time zone
information applies to, e.g. 2006.

### Data Structures

#### SYSTEMTIME structure

The SYSTEMTIME structure is 16 bytes of size and consists of:

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 2 | | Year
2 | 2 | | Month <br/> Where 1 represents January
4 | 2 | | Day of week <br/> Where 0 represents Sunday
6 | 2 | | Day of month <br/> Where 1 represents the first day
8 | 2 | | Hour <br/> Where hour ranges from 0 to 23
10 | 2 | | Minutes <br/> Where minutes ranges from 0 to 59
12 | 2 | | Seconds <br/> Where seconds ranges from 0 to 59
14 | 2 | | Milli seconds <br/> Where milli seconds ranges from 0 to 999

#### Registry Time Zone information structure

The Registry Time Zone information (`TIME_ZONE_INFORMATION` or
`_REG_TZI_FORMAT`) structure is 44 bytes of size and consists of:

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 4 | | Bias <br/> Contains the difference between UTC and local time, in minutes
4 | 4 | | StandardBias <br/> Contains the difference between UTC and local time, in minutes, or 0 if not set
8 | 4 | | DaylightBias <br/>Contains the difference between standard and daylight savings time, in minutes <br/> The total difference is: Bias + DaylightBias
12 | 16 | | StandardDate <br/> Date and time when the daylight savings time switches to standard time, in local time <br/> Contains a SYSTEMTIME structure with year set to 0
28 | 16 | | DaylightDate <br/> Date and time when the standard time switches to daylight savings time, in local time <br/> Contains a SYSTEMTIME structure with year set to 0

The wDayOfWeek member of a SYSTEMTIME structure represents the appropriate
weekday, and the wDay member represents the occurrence of the day of the week
within the month, where 5 indicates the final occurrence during the month if
that day of the week only occurs 4 times in the month.

If the wYear member is 0, the date is relative, meaning the daylight savings
occurs yearly. Otherwise the date is abosule, meaning daylight savings only
changes once.

Note that DaylightBias can be set when DaylightDate is not set.

## External Links

* [Computer Time Management and Embedded Systems (Standard 7 SP1)](https://docs.microsoft.com/en-us/previous-versions/windows/embedded/ff794720(v=winembedded.60))
* [TIME_ZONE_INFORMATION structure (timezoneapi.h)](https://docs.microsoft.com/en-us/windows/win32/api/timezoneapi/ns-timezoneapi-time_zone_information)
* [DYNAMIC_TIME_ZONE_INFORMATION structure (timezoneapi.h)](https://docs.microsoft.com/en-us/windows/win32/api/timezoneapi/ns-timezoneapi-dynamic_time_zone_information)
* [SYSTEMTIME structure (minwinbase.h)](https://docs.microsoft.com/en-us/windows/win32/api/minwinbase/ns-minwinbase-systemtime)
* [windowsZones.xml](https://github.com/unicode-org/cldr/blob/main/common/supplemental/windowsZones.xml)

