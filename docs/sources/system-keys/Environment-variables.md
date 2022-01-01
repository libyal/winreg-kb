# Environment variables

The environment variables are stored in multiple keys.

## Session Manager\\Environment key

```
HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Session Manager\Environment
```

Values:

Name | Data type | Description
--- | --- | ---
%NAME% | REG_SZ | environment variable, where %NAME% contains the name of the environment variable.

For example the "windir" value that contains "%SystemRoot%".

## Windows\\CurrentVersion key

Values of environment variables such as %%ProgramFiles% can be derived from
values in the Windows\\CurrentVersion key:

```
HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion
```

Values:

Name | Data type | Description
--- | --- | ---
CommonFilesDir | REG_SZ | value of %CommonProgramFiles% environment variable
CommonFilesDir (x86) | REG_SZ | value of %CommonProgramFiles(x86)% environment variable
ProgramFilesDir | REG_SZ | value of %ProgramFiles% environment variable
ProgramFilesDir (x86) | REG_SZ | value of %ProgramFiles(x86)% environment variable

For example the "ProgramFilesDir (x86)" value that contains
"C:\Program Files (x86)".

## Windows NT\\CurrentVersion key

The %SystemRoot% environment variable can be derived from values in
the Windows NT\\CurrentVersion key:

```
HKEY_LOCAL_MACHINE\Software\Microsoft\Windows NT\CurrentVersion
```

Values:

Name | Data type | Description
--- | --- | ---
SystemRoot | REG_SZ | value of %SystemRoot% environment variable

For example the "SystemRoot" value that contains "C:\\Windows"

## CurrentVersion\\ProfileList key

Values of environment variables such as %ProgramData% can be derived from
values in the CurrentVersion\\ProfileList key:

```
HKEY_LOCAL_MACHINE\Software\Microsoft\Windows NT\CurrentVersion\ProfileList
```

Values:

Name | Data type | Description
--- | --- | ---
AllUsersProfile | REG_SZ | Value of the %AllUsersProfile% environment variable (Seen on Windows XP)
Default | REG_SZ | (Seen on Windows Vista)
DefaultUserProfile | REG_SZ | (Seen on Windows XP)
ProfilesDirectory | REG_EXPAND_SZ | Profiles directory, for example "C:\Documents and Settings" on Windows XP or "C:\Users" on Windows Vista.
ProgramData | REG_SZ | Value of the %ProgramData% environment variable (Seen on Windows Vista)
Public | REG_SZ |

If the AllUsersProfile value does not start with an environment variable or
an absolute path, but a relative path, it is currently assumed that the value
should be prefixed with the value in ProfilesDirectory.

## User specific environment variables

*TODO add description*

```
HKEY_CURRENT_USER\Environment
```

