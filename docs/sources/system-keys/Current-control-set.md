# Current Control Set

The Windows Registry contains the Current Control Set key:

```
HKEY_LOCAL_MACHINE\System\CurrentControlSet
```

## Current Control Set - Windows 9x/Me

In Windows 9x/Me the Current Control Set key is stored in the SYSTEM.DAT
Registry file.

## Current Control Set - Windows NT

On Windows NT the Current Control Set key is only present at run-time. The
contents of the key is stored in the SYSTEM Registry file and can be
determined by reading the Current value from the key:

```
<RootKey>\Select
```

The Current value contains number of the current control set. Normally 1 or 2 
but other values like 3 or 47 are known to be used. For example a value of 1
maps to the Control Set key:

```
<RootKey>\ControlSet001
```

Normally there are multiple Control Set keys the role each of the Control Set
keys can be different:

> ControlSet001 may be the last control set you booted with, while
> ControlSet002 could be what is known as the last known good control set, or
> the control set that last successfully booted Windows.

These roles are defined by the other values in the Select key:

Value | Data type | Description
--- | --- | ---
Current | REG_DWORD | Current Control Set
Default | REG_DWORD | Default Control Set
Failed | REG_DWORD | Control Set that failed to boot
LastKnownGood | REG_DWORD | Last known good Control Set

### Notes

* Determine if a value of 0 indicates not set
* Confirm if speculations that 9 is the largest value ControlSet00#

