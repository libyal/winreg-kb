# Application compatibility cache

The Application compatibility cache can be found in the following Windows
Registry keys.

In Windows 2000 and XP:

```
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\AppCompatibility
```

In Windows 2003 and later:

```
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\AppCompatCache
```

Note that several sources claim that the Application Compatibility Cache is
part of the [Application Compatibility Database](https://docs.microsoft.com/en-us/windows/win32/devnotes/application-compatibility-database).
However unfortunately these claims are not backed by sources or facts. Since
the previous article does not mention the relationship between the cache and
the database, this document the Application Compatibility Cache to part of
the Windows Application Compatibility subsystem instead.

Note that the actual difference between the Application Compatibility Cache
and Shim (Database) Cache is currently unknown. Be aware that in other sources
the terms can be used interchangeable. Since MSDN explicitly defines
BaseFlushAppcompatCache and ShimFlushCache, there is likely a subtle difference
to what data is cached. Also see: [Understanding Shims](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-7/dd837644(v=ws.10)).

## Windows 2000

Windows 2000 stores Application Compatibility related data in subkeys in:

```
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\AppCompatibility
```

At this time it is unclear if these subkeys serve the same purpose as the
AppCompatCache value in later versions of Windows.

The subkeys are named as the executable files e.g. `Uninstall.exe` and have been
seen to contain the following values:

Name | Data type | Description
--- | --- | ---
%NAME% | | <mark style="background-color: yellow">**Unknown (seen: x, 462)**</mark>
DllPatch-%NAME% | | <mark style="background-color: yellow">**Unknown**</mark>

Also seen values named like `00008 WindowsNT4.0`.

### Windows 2000 unknown value

The Windows 2000 unknown value is variable of size and consists of:

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 4 | 0x0000000c | <mark style="background-color: yellow">**Unknown 1 (header size?)**</mark>
4 | 4 | | <mark style="background-color: yellow">**Unknown 2 (empty values)**</mark>
8 | 4 | | <mark style="background-color: yellow">**Unknown 3**</mark>
12 | 4 | | <mark style="background-color: yellow">**Unknown 4**</mark>

Contains additional data if "Unknown 4 > 0"

```
Empty?
00000000  0c 00 00 00 00 00 00 00  06 00 00 00 00 00 00 00  |................|

With data:
00000000  0c 00 00 00 00 00 00 00  06 00 00 00 04 00 00 00  |................|

00000010  10 00 00 00 00 00 00 00  00 00 15 00 ff ff ff ff  |................|
00000020  ff ff ff ff 0f 00 00 00                           |........(...A.u.|

Sting byte size followed by string:
00000020                           28 00 00 00 41 00 75 00  |........(...A.u.|
00000030  74 00 6f 00 43 00 41 00  44 00 20 00 41 00 70 00  |t.o.C.A.D. .A.p.|
00000040  70 00 6c 00 69 00 63 00  61 00 74 00 69 00 6f 00  |p.l.i.c.a.t.i.o.|
00000050  6e 00 00 00                                       |n.......|

00000050              00 00 00 00                           |n.......|
```

### Windows 2000 DllPatch value

The Windows 2000 DllPatch value is variable of size and contains an UTF-16
little-endian formatted string with end-of-string character e.g. 'shcmn.dll 7'.

<mark style="background-color: yellow">**It is currently unclear what the trailing number represents.**</mark>

## Windows XP

Windows XP stores the application compatibility cache in the value:
AppCompatCache.

The value data consists of:

* header
  * array of LRU cache entry index values
* array of cache entries (suggested that the maximum is 92)

Note that 64-bit versions of Windows XP will use the Windows 2003 64-bit format.

### Windows XP application compat cache header

The Windows XP application compat cache header is 400 bytes of size and
consists of:

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 4 | 0xef, 0xbe, 0xad, 0xde | Signature
4 | 4 | | Number of cached entries
8 | 4 | | Number of LRU array entries
12 | 4 | | <mark style="background-color: yellow">**Unknown (empty values)**</mark>
16 | ... | | LRU array <br> Contains 32-bit value of the index within the array of cache entries <br> <mark style="background-color: yellow">**Currently it is unclear if the top or the bottom of the array is the LRU**</mark>
... | ... | | <mark style="background-color: yellow">**Unknown (padding?)**</mark> <br> Contains 0-byte values

### Windows XP 32-bit application compat cache entry

The Windows XP 32-bit application compat cache entry is 552 bytes of size and consists of:

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 2 x ( MAX_PATH + 4 ) = 528 | | Path <br> UTF-16 little-endian string with end-of-character <br> Note that the unused bytes can contain remnant data
528 | 8 | | Last modification time <br> Contains a FILETIME
536 | 8 | | File size
544 | 8 | | Last update time <br> Contains a FILETIME

Note that the last modification time applies to that of the file e.g. for NTFS
this is the last modified time of the file as stored in the
$STANDARD_INFORMATION attribute.

## Windows 2003

Windows 2003 stores the application compatibility cache in the value: AppCompatCache

The value data consists of:

* header
* array of cache entries (suggested that the maximum is 512)
* string data

### Windows 2003 application compat cache header

The Windows 2003 application compat cache header is 8 bytes of size and consists of:

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 4 | 0xfe, 0x0f, 0xdc, 0xba | Signature
4 | 4 | | Number of cached entries

### Windows 2003 32-bit application compat cache entry

The Windows 2003 32-bit application compat cache entry is 24 bytes of size and consists of:

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 2 | | Path size
2 | 2 | | Maximum path size
4 | 4 | | Path offset <br> The offset value is relative to the start of the header
8 | 8 | | Last modification time <br> Contains a FILETIME
16 | 8 | | File size

Note that the last modification time applies to that of the file e.g. for NTFS
this is the last modified time of the file as stored in the
$STANDARD_INFORMATION attribute.

### Windows 2003 64-bit application compat cache entry

The Windows 2003 64-bit application compat cache entry is 32 bytes of size and consists of:

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 2 | | Path size
2 | 2 | | Maximum path size
4 | 4 | | <mark style="background-color: yellow">**Unknown (padding)**</mark>
8 | 8 | | Path offset <br> The offset value is relative to the start of the header
16 | 8 | | Last modification time <br> Contains a FILETIME
24 | 8 | | File size

Note that the last modification time applies to that of the file e.g. for NTFS
this is the last modified time of the file as stored in the
$STANDARD_INFORMATION attribute.

## Windows Vista and 2008

Windows Vista and 2008 store the application compatibility cache in the value: AppCompatCache

The value data consists of:

* header
* array of cache entries (suggested that the maximum is 1024)
* string data

[NOTE]
If the cache is empty it will only consists of a header.
 
### Windows Vista application compat cache header

The Windows Vista application compat cache header is 8 bytes of size and consists of:

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 4 | 0xfe, 0x0f, 0xdc, 0xba | Signature
4 | 4 | | Number of cached entries

### Windows Vista 32-bit application compat cache entry

The Windows Vista 32-bit application compat cache entry is 24 bytes of size and consists of:

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 2 | | Path size
2 | 2 | | Maximum path size
4 | 4 | | Path offset <br> The offset value is relative to the start of the header
8 | 8 | | Last modification time <br> Contains a FILETIME
16 | 4 | | Insertion flags
20 | 4 | | Shim flags

Note that the last modification time applies to that of the file e.g. for NTFS
this is the last modified time of the file as stored in the
$STANDARD_INFORMATION attribute.

### Windows Vista 64-bit application compat cache entry

The Windows Vista 64-bit application compat cache entry is 32 bytes of size and consists of:

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 2 | | Path size
2 | 2 | | Maximum path size
4 | 4 | | <mark style="background-color: yellow">**Unknown (padding)**</mark>
8 | 8 | | Path offset <br> The offset value is relative to the start of the header
16 | 8 | | Last modification time <br> Contains a FILETIME
24 | 4 | | Insertion flags
28 | 4 | | Shim flags

Note that the last modification time applies to that of the file e.g. for NTFS
this is the last modified time of the file as stored in the
$STANDARD_INFORMATION attribute.

## Windows 7 and 2008 R2

Windows 7 and 2008 R2 store the application compatibility cache in the value: AppCompatCache

The value data consists of:

* header
* array of cache entries (suggested that the maximum is 1024)
* data
* string data

### Windows 7 application compat cache header

The Windows 7 application compat cache header is 128 bytes of size and consists of:

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 4 | 0xee, 0x0f, 0xdc, 0xba | Signature
4 | 4 | | Number of cached entries
8 | 4 | 120 | <mark style="background-color: yellow">**Unknown (size?)**</mark>
12 | 116 | | <mark style="background-color: yellow">**Unknown (cache statistics?)**</mark>

### Windows 7 32-bit application compat cache entry

The Windows 7 32-bit application compat cache entry is 32 bytes of size and consists of:

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 2 | | Path size <br> The byte of the path without the end-of-string character
2 | 2 | | Maximum path size <br> The byte of the path with the end-of-string character
4 | 4 | | Path offset <br> The offset value is relative to the start of the header
8 | 8 | | Last modification time <br> Contains a FILETIME
16 | 4 | | Insertion flags
20 | 4 | | Shim flags
24 | 4 | | Data size
28 | 4 | | Data offset <br> The offset value is relative to the start of the header

Note that the last modification time applies to that of the file e.g. for NTFS
this is the last modified time of the file as stored in the
$STANDARD_INFORMATION attribute.

### Windows 7 64-bit application compat cache entry

The Windows 7 64-bit application compat cache entry is 48 bytes of size and consists of:

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 2 | | Path size <br> The byte of the path without the end-of-string character
2 | 2 | | Maximum path size <br> The byte of the path with the end-of-string character
4 | 4 | | <mark style="background-color: yellow">**Unknown (padding)**</mark>
8 | 8 | | Path offset <br> The offset value is relative to the start of the header
16 | 8 | | Last modification time <br> Contains a FILETIME
24 | 4 | | Insertion flags
28 | 4 | | Shim flags
32 | 8 | | Data size
40 | 8 | | Data offset <br> The offset value is relative to the start of the header

Note that the last modification time applies to that of the file e.g. for NTFS
this is the last modified time of the file as stored in the
$STANDARD_INFORMATION attribute.

## Windows 8

Windows 8 store the application compatibility cache in the value: AppCompatCache

The value data consists of:

* header
* array of cache entries

### Windows 8 application compat cache header

The Windows 8 application compat cache header is 128 bytes of size and consists of:

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 4 | 128 | Header size (or cache entry array offset)
4 | 4 | | <mark style="background-color: yellow">**Unknown**</mark>
8 | 120 | | <mark style="background-color: yellow">**Unknown**</mark>

### Windows 8.0 application compat cache entry

The Windows 8.0 application compat cache entry is variable bytes of size and consists of:

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 4 | "00ts" | Signature
4 | 4 | | <mark style="background-color: yellow">**Unknown**</mark>
8 | 4 | | Cache entry data size <br> The size of the cache entry without the first 12 bytes
12 | 2 | | Path size
14 | ... | | Path <br> UTF-16 little-endian string without end-of-character
... | 4 | | <mark style="background-color: yellow">**Unknown (Insertion flags?)**</mark>
... | 4 | | <mark style="background-color: yellow">**Unknown (Shim flags?)**</mark>
... | 8 | | Last modification time <br> Contains a FILETIME
... | 4 | | Data size
... | ... | | Data

Note that the last modification time applies to that of the file e.g. for NTFS
this is the last modified time of the file as stored in the
$STANDARD_INFORMATION attribute.

### Windows 8.1 application compat cache entry

The Windows 8.1 application compat cache entry is variable bytes of size and consists of:

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 4 | "10ts" | Signature
4 | 4 | | <mark style="background-color: yellow">**Unknown**</mark>
8 | 4 | | Cache entry data size <br> The size of the cache entry without the first 12 bytes
12 | 2 | | Path size
14 | ... | | Path <br> UTF-16 little-endian string without end-of-character
... | 4 | | <mark style="background-color: yellow">**Unknown (Insertion flags?)**</mark>
... | 4 | | <mark style="background-color: yellow">**Unknown (Shim flags?)**</mark>
... | 2 | | <mark style="background-color: yellow">**Unknown**</mark>
... | 8 | | Last modification time <br> Contains a FILETIME
... | 4 | | Data size
... | ... | | Data

Note that the last modification time applies to that of the file e.g. for NTFS
this is the last modified time of the file as stored in the
$STANDARD_INFORMATION attribute.

## Windows 10

Windows 10 store the application compatibility cache in the value: AppCompatCache

The value data consists of:

* header
* array of cache entries

### Windows 10 application compat cache header

The Windows 10 application compat cache header is 48 bytes of size and consists of:

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 4 | 48 | Header size (or cache entry array offset)
4 | 4 | | <mark style="background-color: yellow">**Unknown**</mark>
8 | 4 | | <mark style="background-color: yellow">**Unknown (empty values)**</mark>
12 | 4 | | <mark style="background-color: yellow">**Unknown**</mark>
16 | 4 | | <mark style="background-color: yellow">**Unknown**</mark>
20 | 16 | | <mark style="background-color: yellow">**Unknown (empty values)**</mark>
36 | 4 | | Number of cached entries
40 | 8 | | <mark style="background-color: yellow">**Unknown (empty values)**</mark>

The Windows 10 Creator update application compat cache header is 52 bytes of
size and consists of:

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 4 | 52 | Header size (or cache entry array offset)
4 | 4 | | <mark style="background-color: yellow">**Unknown**</mark>
8 | 4 | | <mark style="background-color: yellow">**Unknown (empty values)**</mark>
12 | 4 | | <mark style="background-color: yellow">**Unknown**</mark>
16 | 4 | | <mark style="background-color: yellow">**Unknown**</mark>
20 | 8 | | <mark style="background-color: yellow">**Unknown (empty values)**</mark>
28 | 4 | | <mark style="background-color: yellow">**Unknown**</mark>
32 | 8 | | <mark style="background-color: yellow">**Unknown (empty values)**</mark>
40 | 4 | | Number of cached entries
44 | 8 | | <mark style="background-color: yellow">**Unknown (empty values)**</mark>

### Windows 10 application compat cache entry

The Windows 10 application compat cache entry is variable bytes of size and consists of:

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 4 | "10ts" | Signature
4 | 4 | | <mark style="background-color: yellow">**Unknown**</mark>
8 | 4 | | Cache entry data size <br> The size of the cache entry without the first 12 bytes
12 | 2 | | Path size
14 | ... | | Path <br> UTF-16 little-endian string without end-of-character
... | 8 | | Last modification time <br> Contains a FILETIME
... | 4 | | Data size
... | ... | | Data

Note that the last modification time applies to that of the file e.g. for NTFS
this is the last modified time of the file as stored in the
$STANDARD_INFORMATION attribute.

## Insertion flags

<mark style="background-color: yellow">**TODO describe**</mark>

Value | Identifier | Description
--- | --- | ---
0x00000001 | |
0x00000002 | | <mark style="background-color: yellow">**Indicated as executed by CSRSS.EXE flag**</mark> <br> <mark style="background-color: yellow">**Client/Server Runtime Subsystem (CSRSS)**</mark>
0x00000004 | |
0x00000008 | |
0x00000010 | | <mark style="background-color: yellow">**Unknown (Seen in Windows 8.0, 8.1)**</mark>
0x00000020 | | <mark style="background-color: yellow">**Unknown (Seen in Windows 8.0, 8.1)**</mark>
0x00000040 | | <mark style="background-color: yellow">**Unknown (Seen in Windows 8.0, 8.1)**</mark>
0x00000080 | | <mark style="background-color: yellow">**Unknown (Seen in Windows 8.0, 8.1)**</mark>
| |
0x00010000 | | <mark style="background-color: yellow">**Unknown (Seen in Windows 8.1)**</mark>
0x00020000 | | <mark style="background-color: yellow">**Unknown (Seen in Windows 8.1)**</mark>
0x00030000 | | <mark style="background-color: yellow">**Unknown (Seen in Windows 8.1)**</mark>
0x00040000 | | <mark style="background-color: yellow">**Unknown (Seen in Windows 8.1)**</mark>
0x00100000 | | <mark style="background-color: yellow">**Unknown (Seen in Windows 8.1)**</mark>
0x00200000 | | <mark style="background-color: yellow">**Unknown (Seen in Windows 8.1)**</mark>
0x00400000 | | <mark style="background-color: yellow">**Unknown (Seen in Windows 8.1)**</mark>
0x00800000 | | <mark style="background-color: yellow">**Unknown (Seen in Windows 8.1)**</mark>

## Shim flags

<mark style="background-color: yellow">**TODO describe**</mark>

Value | Identifier | Description
--- | --- | ---
0x00000001 | | <mark style="background-color: yellow">**Unknown (Has data?)**</mark>
| |
0x00000020 | |
| |
0x00000100 | | <mark style="background-color: yellow">**Unknown (Seen in Windows 7)**</mark>
| |
0x00001000 | | <mark style="background-color: yellow">**Unknown (Seen in Windows 7, 8.0)**</mark>
| |
0x00010000 | | <mark style="background-color: yellow">**Unknown (Seen in Windows 8.0, 8.1)**</mark>
0x00020000 | | <mark style="background-color: yellow">**Unknown (Seen in Windows 8.0)**</mark>
| |
0x00100000 | | <mark style="background-color: yellow">**Unknown (Seen in Windows 8.1)**</mark>
0x00200000 | | <mark style="background-color: yellow">**Unknown (Seen in Windows 8.1)**</mark>
| |
0x01000000 | | <mark style="background-color: yellow">**Unknown (Seen in Windows 8.0, 8.1)**</mark>
0x02000000 | | <mark style="background-color: yellow">**Unknown (Seen in Windows 8.0)**</mark>
| |
0x10000000 | | <mark style="background-color: yellow">**Unknown (Seen in Windows 8.1)**</mark>

## Data

<mark style="background-color: yellow">**TODO describe**</mark>

## Notes

```
https://technet.microsoft.com/en-us/library/cc787360(v=ws.10).aspx

Are these related?
0x00000001 MS-DOS-based program
0x00000002 OS/2-based program
0x00000004 Windows-based 16-bit program
0x00000008 Windows-based 32-bit program
0x0000000C Windows-based 16-bit and 32-bit program
0x0000000F Any version of a program
0x00000010 Return user name instead of computer name for GetComputerName.
0x00000020 Return Terminal Server build number instead of Windows 2000 build number for GetVersion.
0x00000040 Synchronize user .ini file to system version.*
0x00000080 Do not substitute user \Windows directory.**
0x00000100 Disable registry mapping for program or registry key.
0x00000200 Per-object user/system global mapping
0x00000400 Return system \Windows directory instead of user \Windows directory for GetWindowsDir.
0x00000800 Limit the reported physical memory for GlobalMemoryStatus.
0x00001000 Log object creation to file.
0x20000000 Do not put program to sleep on unsuccessful keyboard polling (Windows-based 16-bit programs only).
```

Related DLLs:

* apphelp.dll; related to "AppHelp" functionality and Application Compatibility database
* kernel32.dll; base cache management functionality

Is the Application compatibility cache in Windows also referred to as
AppHelpCache?

AppHelp: https://msdn.microsoft.com/en-us/library/bb432181(v=vs.85).aspx

Different shim types? MSIE and RPC shim types?

Related Registry keys:

```
HKLM\Sofware\Microsoft\Windows NT\CurrentVersion\AppCompatFlags
```

## External links

* [Leveraging the Application Compatibility Cache in Forensic Investigations](https://www.fireeye.com/content/dam/fireeye-www/services/freeware/shimcache-whitepaper.pdf), by Andrew Davis, 2012

