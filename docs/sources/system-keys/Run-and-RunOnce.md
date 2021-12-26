# Run and RunOnce

Run and RunOnce keys cause programs to run each time a user logs on. There are
system and per-user Run and RunOnce keys.

## Run and RunOnce keys

System Run and RunOnce keys:

```
HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Run
HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\RunOnce
HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\RunOnceEx
```

Per-user Run and RunOnce keys:

```
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\RunOnce
```

Values:

Name | Data type | Description
--- | --- | ---
%NAME% | REG_SZ | Command to run or run once

### RunOnce\\Setup sub key

Contains first-boot activities after setup or when the Add/Remove Programs 
Wizard was used.

```
HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\RunOnce\Setup
```

## RunServices and RunServicesOnce

Only on Windows 9x/Me.

Run in the background when the logon dialog box first appears, or at the boot 
process stage if there is no logon.

```
HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\RunServices
HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\RunServicesOnce
```

Values:

Name | Data type | Description
--- | --- | ---
%NAME% | REG_SZ | Command to run or run once

## Notes

```
description-string=commandline
```

According to [MSDN](http://msdn.microsoft.com/en-us/library/aa376977(v=vs.85).aspx):

```
By default, the value of a RunOnce key is deleted before the command line is 
run. You can prefix a RunOnce value name with an exclamation point (!) to defer 
deletion of the value until after the command runs. Without the exclamation 
point prefix, if the RunOnce operation fails the associated program will not be 
asked to run the next time you start the computer.

By default, these keys are ignored when the computer is started in Safe Mode. 
The value name of RunOnce keys can be prefixed with an asterisk (*) to force 
the program to run even in Safe mode.
```

```
HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\policies\Explorer\Run
HKEY_CURRENT_USER\Software\Microsoft\Windows NT\CurrentVersion\Windows\Run
```

Installed "Programs and Features"

```
HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Installer
```

## External Links

* [MSDN: Run and RunOnce Registry Keys](http://msdn.microsoft.com/en-us/library/aa376977(v=vs.85).aspx)

