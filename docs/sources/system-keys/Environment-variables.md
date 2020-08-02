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

## User specific environment variables

*TODO add description*

```
HKEY_CURRENT_USER\Environment
```

