# Mounted devices

The mounted devices settings are stored in the key:

```
HKEY_LOCAL_MACHINE\SYSTEM\MountedDevices
```

Seen on:

* Windows 2000
* Windows XP
* Windows 2003
* Windows Vista
* Windows 2008
* Windows 7
* Windows 8.0
* Windows 8.1
* Windows 10
* Windows 11

Value | Data type | Description
--- | --- | ---
%IDENTIFIER% | REG_BINARY | 

Where the following variants of %IDENTIFIER% have been observed:

* "\DosDevices\C:"
* "\??\Volume{01234567-89ab-cdef-0123-456789abcdef}"

Where the value data consist of either:

* Device string value data
* GPT partition value data
* MBR partition value data

## Device string value data

The device string value data is variable of size and consists of:

Offset | Size | Value | Description
--- | --- | --- | ---
0 | ... | | UTF-16 little-endian encoded string, without an end-of-string character

For example:

```
\??\IDE#CdRomQEMU_QEMU_DVD-ROM_______________________1.6.____#5&12345678&0&0.1.0#{01234567-89ab-cdef-0123-456789abcdef}
\??\SCSI#CdRom&Ven_VBOX&Prod_CD-ROM#4&0123456&0&010000#{01234567-89ab-cdef-0123-456789abcdef}
_??_USBSTOR#Disk&Ven_Generic&Prod_Flash_Disk&Rev_8.07#01234567&0#{01234567-89ab-cdef-0123-456789abcdef}
```

## GPT partition value data

The GPT partition value data is 24 bytes of size and consists of:

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 8 | "DMIO:ID:" | Signature, where DMIO is presumed to refer to Disk Manager I/O Driver
8 | 16 | | GUID Partition Table (GPT) partition identifier (little-endian GUID)

## MBR fixed-disk value data

The MBR partition value data is 12 bytes of size and consists of:

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 4 | | Master Boot Record (MBR) Disk identity (signature) (also referred to as disk identifier)
4 | 8 | | Offset of the partition, in bytes, that contains the previously mounted file system

## Notes

The mountvol.exe Windows CLI tool can show information about mounted devices.

