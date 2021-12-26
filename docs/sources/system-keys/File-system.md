# File system

Windows file system settings are stored in the File system key.

```
HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\FileSystem
```

# File System key

Values:

Value | Data type | Description
--- | --- | ---
NtfsAllowExtendedCharacterIn8dot3Name | REG_DWORD |
NtfsDisable8dot3NameCreation | REG_DWORD |
NtfsDisableLastAccessUpdate | REG_DWORD |
NtfsEncryptionService | REG_SZ |
Win31FileSystem | REG_DWORD |
Win95TruncatedExtensions | REG_DWORD |

## NTFS Disable Short (8.3) Filename Creation value

Value | Description
--- | ---
0 | For NTFS short (8.3) filenames are created
1 | For NTFS short (8.3) filenames are *not* created

## NTFS Disable Last Access Time value

Value | Description
--- | ---
0 | For NTFS the last-accessed timestamp of a file is updated whenever the file is opened.
1 | For NTFS the last-accessed timestamp of a file is *not* updated whenever the file is opened.

**TODO the explanation of the values differs between versions of Windows**

The meaning of the value 0 for Windows 2000 according to
[NtfsDisableLastAccessUpdate](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-2000-server/cc959914(v=technet.10)):

```
When listing directories, NTFS updates the last-access timestamp on each
directory it detects, and it records each time change in the NTFS log.
```

In contrast to the meaning of the value 0 for Windows 2003 according to
[NtfsDisableLastAccessUpdate](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2003/cc758569(v=ws.10)):

```
NTFS updates the last-accessed timestamp of a file whenever that file is opened.
```

**TODO value does not exist by default until Windows XP SP3/Vista**

## External Links

### Windows 2000

* [NtfsDisable8dot3NameCreation](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-2000-server/cc959352(v=technet.10))
* [NtfsDisableLastAccessUpdate](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-2000-server/cc959914(v=technet.10))
* [Win31FileSystem](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-2000-server/cc976058(v=technet.10))
* [NtfsEncryptionService](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-2000-server/cc976057(v=technet.10))
* [NtfsAllowExtendedCharacterIn8dot3Name](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-2000-server/cc963196(v=technet.10))

### Windows 2003

* [NtfsAllowExtendedCharacterIn8dot3Name](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2003/cc781607(v=ws.10))
* [NtfsDisable8dot3NameCreation](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2003/cc778996(v=ws.10))
* [NtfsDisableLastAccessUpdate](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2003/cc758569(v=ws.10))
* [NtfsEncryptionService](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2003/cc739602(v=ws.10))
* [Win95TruncatedExtensions](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2003/cc756733(v=ws.10))

