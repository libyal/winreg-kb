# Services and drivers

*TODO fine tune rough notes*

Settings to load/run drivers and services are stored in the Services key:

```
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services
```

Sub keys:

Value | Data type | Description
--- | --- | ---
Name | Description
%NAME% | The driver or service sub key. Where %NAME% corresponds with the name of the driver or service.

## Driver or Service Name sub key

Values:

Value | Data type | Description
--- | --- | ---
DependOnGroup | `REG_MULTI_SZ` | Other groups the device or service is dependent on.
DependOnService | `REG_MULTI_SZ` | Other services the device or service is dependent on.
Description | `REG_SZ` | Description.
DisplayName | `REG_SZ`, `REG_MULTI_SZ` | Display name.
DriverPackageId | |
ErrorControl | `REG_DWORD` | The level of error control.
FailureActions | |
Group | `REG_SZ` | Name of the group the device or service is part of.
ImagePath | `REG_SZ` | Path and filename of device or service executable file (or image).
ObjectName | `REG_SZ` | See section: ObjectName value
RequiredPrivileges | |
Start | `REG_DWORD` | The start control value.
ServiceSidType | |
Tag | `REG_DWORD` |
Type | `REG_DWORD` | The driver or service type.

### ErrorControl value

Value | Identifier | Description
--- | --- | ---
0x00000000 | Ignore |
0x00000001 | Normal |
0x00000002 | Severe |
0x00000003 | Critical |

### ObjectName value

The ObjectName value has a different meaning for different types of Driver or
Service Name sub keys.

* For a driver type the ObjectName value contains the Windows NT driver object name that the I/O Manager uses to load the device driver.
* For a service type the ObjectName value contains the account name under which the service will log on to run.

Windows Services shows this value as "LogOn As".

### Start value

Value | Identifier | Description
--- | --- | ---
0x00000000 | Boot | Driver or service controlled by the kernel that is loaded by the boot loader.
0x00000001 | System | Driver or service controlled by the I/O sub system that is loaded at kernel initialization.
0x00000002 | Automatic | Driver or service controlled by the Services Control Manager that is loaded at start up. Also referred to as: Auto load
0x00000003 | On demand | Driver or service controlled by the Services Control Manager that is loaded on demand. Also referred to as: Load on demand or Automatic (Delayed start)
0x00000004 | Disabled | Driver or service controlled by the Services Control Manager that is disabled.

Windows Services shows this value as "Startup Type".

### Type value

Value | Identifier | Description
--- | --- | ---
0x00000001 | | Kernel device driver
0x00000002 | | File system driver
0x00000004 | | A set of argument for an adapter
0x00000008 | | *Unknown, seen in combination Fs_Rec*
0x00000010 | | Stand-alone (self-contained) service
0x00000020 | | Shared service
0x00000100 | | *Unknown, seen in combination with 0x00000010 and 0x00000020. Goes back to Windows 2000 maybe to indicate a network service.*

