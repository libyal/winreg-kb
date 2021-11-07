# Mounted devices

The mounted devices settings are stored in the key:

```
HKEY_LOCAL_MACHINE\SYSTEM\MountedDevices
```

Value | Data type | Description
--- | --- | ---
%IDENTIFIER% | REG_BINARY | 

Where the following forms of %IDENTIFIER% have been observed:

* "\DosDevices\C:"
* "\??\Volume{01234567-89ab-cdef-0123-456789abcdef}"

Where the value data consist of either:

* Device string value data
* Fixed-disk value data

## Device string value data

The device string value data is variable of size and consists of:

Offset | Size | Value | Description
--- | --- | --- | ---
0 | ... | | UTF-16 little-endian encoded string, without an end-of-string character

For example:

```
\??\SCSI#CdRom&Ven_VBOX&Prod_CD-ROM#4&0123456&0&010000#{01234567-89ab-cdef-0123-456789abcdef}
```

```
_??_USBSTOR#Disk&Ven_Generic&Prod_Flash_Disk&Rev_8.07#01234567&0#{01234567-89ab-cdef-0123-456789abcdef}
```

## Fixed-disk value data

The fixed-disk value data is 12 bytes of size and consists of:

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 4 | | Master Boot Record (MBR) Disk identity (signature) (also referred to as disk identifier)
4 | 8 | | Offset of the partition, in bytes, that contains the previously mounted file system

## Notes

The mountvol.exe Windows CLI tool can show information about mounted devices.

