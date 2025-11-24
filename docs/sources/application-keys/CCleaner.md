# CCleaner

**TODO this page currently contains rough notes, fine tune these**

The CCleaner application uses the following Windows Registry key to store its
configuration.

```
HKEY_CURRENT_USER\Software\Piriform\CCleaner
```

Values:

Name | Data type | Description
--- | --- | ---
(App)Program Name | REG_SZ |
AutoClose | | Automatically close program after cleaning, where 0 = Disabled and 1 = Enabled
BackupDir | | Default path for the Issues Registry back up
BackupPrompt | | Prompts user to back up the contents of the Issues Registry before removing them, where 0 = Disabled and 1 = Enabled
BrowserMonitoring | | Whether automatic browser cleaning is active (CCleaner Professional), where 0 = Disabled and 1 = Enabled
CookiesToSave | REG_SZ | Lists of cookies to preserve
DefaultDetailedView | | Show detailed view screen (for the whole analysis or cleaning) after the operation finishes, where 0 = Disabled and 1 = Enabled
DelayTemp | | Delete temporary (Windows) files older than 48 hours, where 0 = Disabled and 1 = Enabled
FFDetailed | | Display a detailed log of Firefox/Mozilla temporary files, where 0 = Disabled and 1 = Enabled
HideWarnings | | Hide warnings when advanced items is selected in the cleaning options tree, where 0 = Disabled and 1 = Enabled
HomeScreen | | Starts on Health Check or Custom Clean, where 0 = Custom Clean and 1 = Health Check
IEDetailed | | Display a detailed log of Internet Explorer temporary files, where 0 = Disabled and 1 = Enabled
Language | | Language, contains a locale identifier (LCID).
MinimizeSystemTray | | Minimize program to system tray on close, where 0 = Disabled and 1 = Enabled
Monitoring | | Have Smart Cleaning, where 0 = Disabled and 1 = Enabled
MSG_CONFIRMCLEAN | | Ask for confirmation before starting the Cleaning operation, where the value can be "True" or "False"
MSG_WARNCHROMECACHE | | Warn when cleaning the Internet Cache in Google Chrome, where the value can be "True" or "False"
MSG_WARNMOZCACHE | | Warn when cleaning the Internet Cache in Mozilla Firefox, where the value can be "True" or "False"
RunICS | | No longer used, will automatically be set to 0
SecureDeleteMethod | | Secure deletion method, where 0 = Simple Overwrite (1 pass), 1 = DOD 5220.22-M (3 passes), 2 = NSA (7 passes) or 3 = Gutmann (35 passes)
SecureDeleteType | | Use a secure deletion method, where 0 = Disabled and 1 = Enabled
SystemMonitoring | | Activate System Smart Cleaning (or Active Monitoring for CCleaner Professional), where 0 = Disabled and 1 = Enabled
SystemMonitoringSavingsAction | | System Smart Cleaning (or Active Monitoring for CCleaner Professional) mode, where 3 = "prompt to clean", 4 = "auto clean with notification" and 5 = "auto clean without notification"
UpdateBackgroundCheck | | Check for software updates every 10 minutes (after program start), where 0 = Disabled and 1 = Enabled
UpdateKey | REG_SZ | The last update check date and time formatted as: "MM/DD/YYYY hh:mm:ss [A|P]M", for example "07/13/2013 10:03:14 AM".
WINDOW_HEIGHT | REG_SZ | Window height dimension in number of pixels.
WINDOW_LEFT | REG_SZ | Window left position in number of pixels.
WINDOW_MAX | REG_SZ | Windows is maximized, where 0 = not maximized
WINDOW_TOP | REG_SZ | Window top position in number of pixels.
WINDOW_WIDTH | REG_SZ | Window width dimension in number of pixels.
WipeMFTFreeSpace | | Wipe free space in the NTFS Master File Table (MFT), where 0 = Disabled and 1 = Enabled

## (App)Program Name

These entries indicate programs that are not part of the default set of enabled
Cleaning Rules, and whether they should be cleaned.

Note: Making an entry of "App(Your Program)]=true" will not allow CCleaner to
clean it, as you would instead need to use the methods listed here.

True = Checkbox selected when you start CCleaner.
False = Checkbox cleared when you start CCleaner.

Known Cleaning Rules:

* (App)Cookies, contains "True" if the cookies should be cleaned;
* (App)Delete Index.dat files
* (App)History
* (App)Last Download Location
* (App)Other Explorer MRUs
* (App)Recent Documents
* (App)Recently Typed URLs
* (App)Run (in Start Menu)
* (App)Temporary Internet Files
* (App)Thumbnail Cache

## IncludeX (e.g. Include1, Include2)

Custom files or folders that should be included in cleaning

[PATH|FILE]|Path|Filename

## ExcludeX (e.g. Exclude1, Exclude2)

Custom files or folders that should be excluded from cleaning.

[REG|PATH|FILE]|Path|Filename

## FinderIncludeX (e.g. FinderInclude1, FinderInclude2)

Drives or folders CCleaner to use when searching for duplicate files.

PATH|PATH\|Filetype|[RECURSE]

## FinderIncludeStates

Whether the checkboxes have been checked or unchecked for folders referenced
by FinderIncludeX.

0 = Cleared
1 = Selected

For example, if there are three FinderIncludeX statements, you can specify the
checked/cleared status using the pipe symbol:

FinderIncludeStates=1|0|1 would check the first and last items, and the middle
one would be unchecked.

## External Links

* [Writing a CCleaner RegRipper Plugin Part 1](https://cheeky4n6monkey.blogspot.com/2012/02/writing-ccleaner-regripper-plugin-part.html)
* [Writing a CCleaner RegRipper Plugin Part 2](http://cheeky4n6monkey.blogspot.com/2012/02/writing-ccleaner-regripper-plugin-part_05.html)

