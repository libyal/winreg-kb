# Task scheduler

## SchedulingAgent key

In Windows XP:

```
HKEY_LOCAL_MACHINE\Software\Microsoft\SchedulingAgent
```

Values:

Name | Data type | Description
--- | --- | ---
DataVersion | |
LastTaskRun | |
LogPath | |
MaxLogSizeKB | |
MinutesBeforeIdle | |
OldName | |
PriorDataVersion | |
TasksFolder | |

## Schedule key

In Windows Vista and later:

```
HKEY_LOCAL_MACHINE\Software\Microsoft\Windows NT\CurrentVersion\Schedule
```

Sub keys:

Name | Description
--- | ---
Aliases |
CompatibilityAdapter |
Configuration |
CredWom |
Handlers |
Handshake |
TaskCache |

Values:

Name | Data type | Description
--- | --- | ---
DomainJoinDetected | |
HashingCompleted | |
MigrationCleanupCompleted | |

### TaskCache sub key

```
HKEY_LOCAL_MACHINE\Software\Microsoft\Windows NT\CurrentVersion\Schedule\TaskCache
```

Sub keys:

Name | Description
--- | ---
Boot |
Logon |
Plain |
Tasks |
Tree |

#### TaskCache\\Tree sub key

```
HKEY_LOCAL_MACHINE\Software\Microsoft\Windows NT\CurrentVersion\Schedule\TaskCache\Tree
```

Values:

Name | Data type | Description
--- | --- | ---
Id | | Contains a GUID that corresponds to an entry in the Task Cache
Index | |

#### TaskCache\\Tree\\%GUID% sub key

```
HKEY_LOCAL_MACHINE\Software\Microsoft\Windows NT\CurrentVersion\Schedule\TaskCache\Tasks\%GUID%
```

Values:

Name | Data type | Description
--- | --- | ---
DynamicInfo | |
Hash | | Integrity hash of the of XML task file (in %windir%\\System32\\Tasks) <br> Contains a SHA-256 or CRC32, before KB2305420. A byte-order-mark at beginning of the file is not included in the calculation of the hash.
Path | | Path of the corresponding Registry key in the TaskCache Tree sub key
Triggers | |

##### TaskCache\\Tree\\%GUID%\\DynamicInfo sub key

Seen in Windows Vista, Windows 2008 and Windows 7:

The dynamic information entry is 28 bytes of size and consists of:

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 4 | 3 | <mark style="background-color: yellow">**Unknown**</mark>
4 | 8 | | <mark style="background-color: yellow">**Unknown timestamp (last registered or update time?)**</mark> <br> Contains a FILETIME or 0 if not set
12 | 8 | | <mark style="background-color: yellow">**Unknown timestamp (launch time?)**</mark> <br> Contains a FILETIME or 0 if not set
20 | 4 | | <mark style="background-color: yellow">**Unknown (flags?)**</mark>
24 | 4 | | <mark style="background-color: yellow">**Unknown (empty values)**</mark>

```
0x00000000  03 00 00 00 1c ec 45 16  3f 04 ca 01 00 00 00 00  ......E.?.......
0x00000010  00 00 00 00 00 00 00 00  00 00 00 00              ............

0x00000000  03 00 00 00 16 6f 4a 0f  7f fe c6 01 66 b7 6c 0d  .....oJ.....f.l.
0x00000010  6b 4c c9 01 2b 04 07 80  00 00 00 00              kL..+.......
```

Seen in Windows 8 and Windows 10:

<mark style="background-color: yellow">**TODO: check Windows 2012**</mark>

The dynamic information entry is 36 bytes of size and consists of:

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 4 | 3 | <mark style="background-color: yellow">**Unknown**</mark>
4 | 8 | | <mark style="background-color: yellow">**Unknown timestamp (last registered or update time?)**</mark> <br> Contains a FILETIME or 0 if not set
12 | 8 | | <mark style="background-color: yellow">**Unknown timestamp (launch time?)**</mark> <br> Contains a FILETIME or 0 if not set
20 | 4 | | <mark style="background-color: yellow">**Unknown (flags?)**</mark>
24 | 4 | | <mark style="background-color: yellow">**Unknown (empty values)**</mark>
28 | 8 | | <mark style="background-color: yellow">**Unknown timestamp**</mark> <br> Contains a FILETIME or 0 if not set

```
0x00000000  03 00 00 00 4b 5a 0b 60  ff 6a cd 01 5c 32 e7 45  ....KZ.`.j..\2.E
0x00000010  1b b6 ce 01 20 04 07 80  00 00 00 00 a2 b1 86 4f  .... ..........O
0x00000020  1b b6 ce 01                                       ....
```

##### Path value

The path value is relative from:

```
HKEY_LOCAL_MACHINE\Software\Microsoft\Windows NT\CurrentVersion\Schedule\TaskCache\Tree
```

For example the path:

```
\Microsoft\Windows\Media Center\ehDRMInit
```

Corresponds to:

```
HKEY_LOCAL_MACHINE\Software\Microsoft\Windows NT\CurrentVersion\Schedule\TaskCache\Tree\Microsoft\Windows\Media Center\ehDRMInit
```

##### Triggers value

Note that the FILETIME value appear to be stored in local time.

