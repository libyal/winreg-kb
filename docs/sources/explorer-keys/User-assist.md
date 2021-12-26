# User Assist key

The User Assist key contains settings and data of programs that were launched
via Windows Explorer (explorer.exe).

```
HKEY_CURRENT_USER\Software\Microsoft\Windows\Currentversion\Explorer\UserAssist
```

Sub keys:

Name | Description
--- | ---
{%GUID%} | The User Assist logged data
Settings | Settings to control User Assist logging

Note that the Settings sub key does not exist by default.

## Known GUIDs

GUID | Windows Versions | Description
--- | --- | ---
{0D6D4F41-2994-4BA0-8FEF-620E43CD2812} | XP, Vista | *TODO assumed as: IE7*
{5E6AB780-7743-11CF-A12B-00AA004AE837} | 2000, XP, 2003, Vista | Microsoft Internet Toolbar
{75048700-EF1F-11D0-9888-006097DEACF9} | 2000, XP, 2003, Vista | ActiveDesktop
{9E04CAB2-CC14-11DF-BB8C-A2F1DED72085} | 8, 10 |
{A3D53349-6E61-4557-8FC7-0028EDCEEBF6} | 8, 10 |
{B267E3AD-A825-4A09-82B9-EEC22AA3B847} | 8 |
{BCB48336-4DDD-48FF-BB0B-D3190DACB3E2} | 8.1 |
{CAA59E3C-4792-41A5-9909-6A6A8D32490E} | 8 |
{CEBFF5CD-ACE2-4F4F-9178-9926F41749EA} | 2008 (R2?), 7, 8, 10 | *TODO assumed as: Application or Executable File Execution*
{F2A1CB5A-E3CC-4A2E-AF9D-505A7009D442} | 8, 10 |
{F4E57C4B-2036-45F0-A9AB-443BCFE33D9F} | 2008 (R2?), 7, 8, 10 | *TODO assumed as: Shortcut File Execution*
{FA99DFC7-6AC2-453A-A5E2-5E2AFF4507BD} | 8, 10 |

Note that the User Assist key does not seem to be present on NT4, therefore this
functionality was likely introduced in Windows 2000.

Sometimes more information about the GUID can be found in the key:

```
HKEY_LOCAL_MACHINE\Software\Classes\CLSID\{%GUID%}\
```

## GUID sub key

Sub keys:

Name | Description
--- | ---
Count | Contains the User Assist log entries

Values:

Name | Data type | Description
--- | --- | ---
Version | REG_DWORD | Indicates the User Assist log format version

### Version value data

Value | Windows Versions
--- | ---
3 | 2000, XP, 2003, Vista
5 | 2008 (R2?), 7, 8

### Count sub key

Values:

Name | Data type | Description
--- | --- | ---
%NAME% | REG_SZ | Where %NAME% is obfuscated using a technique described below.

Windows Versions | Obfuscation technique
--- | ---
2000, XP, 2003, Vista, 2008 (R2?), 7, 8 | ROT-13 of character values in the ASCII `[A-Za-z]` range. +
Values outside of this range e.g. `[0-9]` and values outside the basic ASCII range (>= 0x80) are not obfuscated.
7 beta | Vigenère cipher with key: BWHQNKTEZYFSLMRGXADUJOPIVC

#### Named value

Value | Description
--- | ---
UEME_CTLSESSION | Session identifier
UEME_CTLCUACount:ctor |
UEME_RUNCPL | Executed control applets (.cpl)
UEME_RUNPATH | Executed programs
UEME_RUNPIDL | Programs started via a PIDL (shell item list) e.g. using a Shortcut
UEME_RUNWMCMD | Programs started via a Run Command
UEME_UIHOTKEY | Programs started via a Hotkey
UEME_UIQCUT | Programs started via a Quick Launch menu shortcut
UEME_UISCUT | Programs started via a Desktop shortcut
UEME_UITOOLBAR | Programs started via Windows Explorer Toolbar buttons

Note does UEME stand for User Experience Monitoring Element/Extension?
Note does CTL stand for client?
Note does CUA stand for current user (file) associations?

With the exception of the UEME_CTLSESSION value, these values appear to use
a similar data types. The structure of a data type depends on the Version value
of the GUID sub key. The following versions have been observed:

* version 3, that is used by Windows 2000, XP, 2003 and Vista.
* version 5, that is used by Windows 2008 (R2?), 7, 8.

#### UEME_CTLSESSION value data

##### UEME_CTLSESSION value data - version 3

The UEME_CTLSESSION value data - version 3 is 8 bytes of size and consists of:

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 4 | | Unknown
4 | 4 | | Current session identifier

##### UEME_CTLSESSION value data - version 5

The UEME_CTLSESSION value data - version 5 is 1612 bytes of size and consists of:

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 4 | 1 | Unknown (version?)
4 | 4 | | Unknown
8 | 4 | | Unknown
12 | 4 | | Unknown
16 | ... | | Unknown (array of 3x records at offset 0x10, 0x224, 0x438)

The UEME_CTLSESSION value data - version 5 record is 532 bytes of size and consists of:

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 4 | | Unknown
8 | 4 | | Unknown
12 | 4 | | Unknown
16 | ... | | Unknown (UTF-16 little-endian string with end-of-string character)
... | ... | | Unknown

#### Other value data

##### Other value data - version 3

The other value data - version 3 is 16 bytes of size and consists of:

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 4 | | Session identifier
4 | 4 | | Number of executions
8 | 8 | | Last execution time, which contains a FILETIME

##### Other value data - version 5

The other value data - version 5 is 72 bytes of size and consists of:

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 4 | | Unknown (Seen: 0, -1 (0xffffffff) or 1)
4 | 4 | | Number or executions
8 | 4 | | Unknown (sometimes referred to as number of application focuses)
12 | 4 | | Unknown (sometimes referred to as application focus time, does its meaning differ per GUID?)
16 | 4 | | Unknown (Contains a 32-bit floating point, 0.0 or -1.0 if not set ?)
20 | 4 | | Unknown (Contains a 32-bit floating point, 0.0 or -1.0 if not set ?)
24 | 4 | | Unknown (Contains a 32-bit floating point, 0.0 or -1.0 if not set ?)
28 | 4 | | Unknown (Contains a 32-bit floating point, 0.0 or -1.0 if not set ?)
32 | 4 | | Unknown (Contains a 32-bit floating point, 0.0 or -1.0 if not set ?)
36 | 4 | | Unknown (Contains a 32-bit floating point, 0.0 or -1.0 if not set ?)
40 | 4 | | Unknown (Contains a 32-bit floating point, 0.0 or -1.0 if not set ?)
44 | 4 | | Unknown (Contains a 32-bit floating point, 0.0 or -1.0 if not set ?)
48 | 4 | | Unknown (Contains a 32-bit floating point, 0.0 or -1.0 if not set ?)
52 | 4 | | Unknown (Contains a 32-bit floating point, 0.0 or -1.0 if not set ?)
56 | 4 | | Unknown, sometimes -1 (0xffffffff)
60 | 8 | | Last execution time, contains a FILETIME or 0 if not set
68 | 4 | 0 | Unknown (empty value ?)

## Settings sub key

Values:

Name | Data type | Description
--- | --- | ---
NoLog | REG_DWORD | Turn of logging. Set to 1 to disable logging of the User Assist information
NoEncrypt | REG_DWORD | Turn of obfuscation of %NAME% values. Set to 1 to disable name obfuscation

## External links

* [UserAssist](https://blog.didierstevens.com/programs/userassist), by Didier Stevens
* [Windows 7 Beta: ROT13 Replaced With Vigenère? Great Joke!](https://blog.didierstevens.com/2009/01/18/quickpost-windows-7-beta-rot13-replaced-with-vigenere-great-joke/)
* [Windows-userassist-keys](https://www.aldeid.com/wiki/Windows-userassist-keys)
* [libfwsi: Known Folder Identifiers](https://github.com/libyal/libfwsi/wiki/Known-Folder-Identifiers)

