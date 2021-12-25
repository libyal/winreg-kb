# Boot Verification key

```
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\BootVerification
```

The BootVerification key stores configuration for Bootvrfy.exe, a program
included in Windows Server 2003 that notifies the system that startup was
successful. Bootvrfy.exe can be run on a local or remote computer.

Known values of the BootVerification key:

Value | Data type | Description
--- | --- | ---
ErrorControl | REG_DWORD | Known value: 1
%SERVICE%\ImagePath | REG_EXPAND_SZ | Known value: "Bootvrfy.exe"
ObjectName | REG_SZ | Known value: "LocalSystem"
Start Entry | REG_DWORD | Known value: 3
Type Entry | REG_DWORD | Known value: 2

To run a custom startup verification program the standard startup verification
functions in Winlogon need to be disabled. This can be done by setting the
Winlogon ReportBootOk value to 0.

```
HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon
```

## Boot Verification Program key

```
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\BootVerificationProgram
```

The BootVerificationProgram key stores configuration for a custom startup
verification program.

Known values of the BootVerificationProgram key:

Value | Data type | Description
--- | --- | ---
ImagePath | REG_SZ, REG_EXPAND_SZ | path of a custom startup verification program

According Windows server 2003 documentation Bootvrfy.exe and a custom startup
verification program cannot be used in parallel.

## External links

* [BootVerification](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2003/cc778559(v=ws.10))
* [BootVerificationProgram](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2003/cc782537(v=ws.10))
* [BootVerificationProgram\ImagePath](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2003/cc786702(v=ws.10))
* [ReportBootOk](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2003/cc739989(v=ws.10))

