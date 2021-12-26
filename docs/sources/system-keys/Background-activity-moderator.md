# Background activity moderator (BAM)

The Background Activity Moderator (BAM) key seems to have been introduced in
Windows 10 after version 1709.

The BAM keys can be found in the following Registry paths:

```
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\bam\UserSettings\
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\bam\State\UserSettings\
```

Within the UserSettings key, there is a key for each user SID containing
a value for each tracked executable.

## Example Entry

Registry Key:

```
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\bam\State\UserSettings\S-1-5-21-321011808-3761883066-353627080-1000
```

Value Name:

```
\Device\HarddiskVolume1\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
```

Value Data:

```
00000000  15 3e ae 36 57 de d4 01 00 00 00 00 00 00 00 00  |.>®6WÞÔ.........|
00000010  00 00 00 00 02 00 00 00                          |........|
```

## Value Data Format

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 8 | | Execution time <br> Contains a FILETIME
8 | 8 | | <mark style="background-color: yellow">**Unknown (empty values)**</mark>
16 | 4 | | Flag indicating whether the entry is a "Windows app"
20 | 4 | 0x02, 0x00, 0x00, 0x00 | <mark style="background-color: yellow">**Unknown (always 2)**</mark>
