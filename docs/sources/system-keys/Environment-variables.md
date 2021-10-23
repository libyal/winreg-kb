# Environment variables

The environment variables are stored in the key:

```
HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Session Manager\Environment\
```

The names of the values in this key represent the name of the environment
variable, for example the "windir" value that contains the follow string:

```
%SystemRoot%
```

## SystemRoot environment variable

The value of %SystemRoot% environment variable is stored in the SystemRoot
value of the following Registry key:

```
HKEY_LOCAL_MACHINE\Software\Microsoft\Windows NT\CurrentVersion
```

On Windows NT this key is stored in the SOFTWARE Registry file as:

```
<RootKey>\Microsoft\Windows NT\CurrentVersion
```

The contents of the value should be a string, for example:

```
C:\Windows\
```

*TODO describe PathName value*

### Profile path environment variables

Values of environment variables such as %AllUsersProfile% and %ProgramData% can
be derived from values in the the ProfileList key:

```
HKEY_LOCAL_MACHINE\Software\Microsoft\Windows NT\CurrentVersion\ProfileList
```

Values:

Value | Data type | Description
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

