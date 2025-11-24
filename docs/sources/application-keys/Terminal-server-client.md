# Terminal server client

The most recent used (MRU) connnections of the Terminal server client can
be found in the key:

```
HKEY_CURRENT_USER\Software\Microsoft\Terminal Server Client\Default
```

Values:

Name | Data type | Description
--- | --- | ---
MRU# | REG_SZ | The most recently used connection. <br> Where # is a string in the form: "[0-9]+"

The contents of MRU# is either an IP address, e.g. 192.168.16.60, or a hostname, e.g. computer.domain.com.

## External Links

* [How to Remove Entries from the Remote Desktop Connection Computer Box](https://learn.microsoft.com/en-us/troubleshoot/windows-server/remote/remove-entries-from-remote-desktop-connection-computer)

