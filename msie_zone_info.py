#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Script to print the MSIE zone information in the Windows Registry
# from the NTUSER.DAT or SOFTWARE Registry file (REGF)
#
# Copyright (c) 2013, Joachim Metz <joachim.metz@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys

import pyregf

DEFAULT_ZONE_NAMES = {
	"0": "My Computer",
	"1": "Local Intranet Zone",
	"2": "Trusted sites Zone",
	"3": "Internet Zone",
	"4": "Restricted Sites Zone",
}

# Sources:
# http://support.microsoft.com/kb/182569
# http://technet.microsoft.com/en-us/library/cc783259(v=ws.10).aspx
CONTROL_DESCRIPTIONS = {
	"1001": "Download signed ActiveX controls",
	"1004": "Download unsigned ActiveX controls",
	"1200": "Run ActiveX controls and plug-ins",
	"1201": "Initialize and script ActiveX controls not marked as safe for scripting",
	"1206": "Allow scripting of Internet Explorer Web browser control",
	"1207": "Reserved",
	"1208": "Allow previously unused ActiveX controls to run without prompt",
	"1209": "Allow Scriptlets",
	"120A": "Override Per-Site (domain-based) ActiveX restrictions",
	"120B": "Override Per-Site (domain-based) ActiveX restrictions",
	"1400": "Active scripting",
	"1402": "Scripting of Java applets",
	"1405": "Script ActiveX controls marked as safe for scripting",
	"1406": "Access data sources across domains",
	"1407": "Allow Programmatic clipboard access",
	"1408": "Reserved",
	"1601": "Submit non-encrypted form data",
	"1604": "Font download",
	"1605": "Run Java",
	"1606": "Userdata persistence",
	"1607": "Navigate sub-frames across different domains",
	"1608": "Allow META REFRESH",
	"1609": "Display mixed content",
	"160A": "Include local directory path when uploading files to a server",
	"1800": "Installation of desktop items",
	"1802": "Drag and drop or copy and paste files",
	"1803": "File Download",
	"1804": "Launching programs and files in an IFRAME",
	"1805": "Launching programs and files in webview",
	"1806": "Launching applications and unsafe files",
	"1807": "Reserved",
	"1808": "Reserved",
	"1809": "Use Pop-up Blocker",
	"180A": "Reserved",
	"180B": "Reserved",
	"180C": "Reserved",
	"180D": "Reserved",
	"1A00": "Logon",
	"1A02": "Allow persistent cookies that are stored on your computer",
	"1A03": "Allow per-session cookies (not stored)",
	"1A04": "Don't prompt for client certificate selection when no certificates or only one certificate exists",
	"1A05": "Allow 3rd party persistent cookies",
	"1A06": "Allow 3rd party session cookies",
	"1A10": "Privacy Settings",
	"1C00": "Java permissions",
	"1E05": "Software channel permissions",
	"1F00": "Reserved",
	"2000": "Binary and script behaviors",
	"2001": "Run components signed with Authenticode",
	"2004": "Run components not signed with Authenticode",
	"2100": "Open files based on content, not file extension",
	"2101": "Web sites in less privileged web content zone can navigate into this zone",
	"2102": "Allow script initiated windows without size or position constraints",
	"2103": "Allow status bar updates via script",
	"2104": "Allow websites to open windows without address or status bars",
	"2105": "Allow websites to prompt for information using scripted windows",
	"2200": "Automatic prompting for file downloads",
	"2201": "Automatic prompting for ActiveX controls",
	"2300": "Allow web pages to use restricted protocols for active content",
	"2301": "Use Phishing Filter",
	"2400": ".NET Framework: XAML browser applications",
	"2401": ".NET Framework: XPS documents",
	"2402": ".NET Framework: Loose XAML",
	"2500": "Turn on Protected Mode [Vista only setting]",
	"2600": "Enable .NET Framework setup",
}

CONTROL_VALUES_COMMON_ENABLE = {
	0x00000000: "Enable",
	0x00000001: "Prompt",
	0x00000003: "Disable",
	0x00010000: "Administrator approved",
}

CONTROL_VALUES_COMMON_SAFETY = {
	0x00010000: "High safety",
	0x00020000: "Medium safety",
	0x00030000: "Low safety",
}

CONTROL_VALUES_1A00 = {
	0x00000000: "Automatic logon with current user name and password",
	0x00010000: "Prompt for user name and password",
	0x00020000: "Automatic logon only in Intranet zone",
	0x00030000: "Anonymous logon",
}

CONTROL_VALUES_1C00 = {
	0x00000000: "Disable Java",
	0x00010000: "High safety",
	0x00020000: "Medium safety",
	0x00030000: "Low safety",
	0x00800000: "Custom",
}

def PrintUsage():
	print "Usage: ./msie_zone_info.py registry_file"
	print ""
	print "   	registry_file: The path of the NTUSER.DAT or SOFTWARE registry file."
	print ""

def PrintZonesKey( regf_file, zones_key_path, output_mode = 0 ):
	zones_key = regf_file.get_key_by_path( zones_key_path )

	if zones_key:
		print "Key: %s" %( zones_key_path )
		print ""

		for zone_key in zones_key.sub_keys:
			# TODO: the zone names are defined in another key.
			if zone_key.name in DEFAULT_ZONE_NAMES:
				print "Zone: %s: %s" %( zone_key.name, DEFAULT_ZONE_NAMES[ zone_key.name ] )
			else:
				print "Zone: %s" %( zone_key.name )

			for setting_value in zone_key.values:
				if not setting_value.name:
					next

				elif setting_value.name in [ "Description", "DisplayName", "PMDisplayName" ]:
					if output_mode == 0:
						print "%s: %s" %( setting_value.name, setting_value.data_as_string )

				elif ( len( setting_value.name ) == 4 and setting_value.name != "Icon" ):
					if len( setting_value.data ) != 4:
						if output_mode == 0:
							print "Value: %s" %( setting_value.data.encode( "hex" ) )

					else:
						value = setting_value.get_data_as_integer()

						value_desc = ""

						if setting_value.name in [
						    "1001", "1004", "1200", "1201", "1400", "1402", "1405", "1406", "1407",
						    "1601", "1604", "1606", "1607", "1608", "1609", "1800", "1802", "1803",
						    "1804", "1809", "1A04", "2000", "2001", "2004", "2100", "2101", "2102",
						    "2200", "2201", "2300" ]:
							if value in CONTROL_VALUES_COMMON_ENABLE:
								value_desc = CONTROL_VALUES_COMMON_ENABLE[ value ]

						elif setting_value.name == "1A00":
							if value in CONTROL_VALUES_1A00:
								value_desc = CONTROL_VALUES_1A00[ value ]

						elif setting_value.name == "1C00":
							if value in CONTROL_VALUES_1C00:
								value_desc = CONTROL_VALUES_1C00[ value ]

						elif setting_value.name == "1E05":
							if value in CONTROL_VALUES_COMMON_SAFETY:
								value_desc = CONTROL_VALUES_COMMON_SAFETY[ value ]

					if output_mode == 0:
						if setting_value.name in CONTROL_DESCRIPTIONS:
							print "Control: %s: %s" %( setting_value.name, CONTROL_DESCRIPTIONS[ setting_value.name ] )
						else:
							print "Control: %s" %( setting_value.name )
						if value_desc:
							print "Data: 0x%08x: %s" %( value, value_desc )
						else:
							print "Data: 0x%08x" %( value )
					elif output_mode == 1:
						if setting_value.name in CONTROL_DESCRIPTIONS:
							control_desc = CONTROL_DESCRIPTIONS[ setting_value.name ]
						else:
							control_desc = ""
						print "%s\t0x%08x\t%s\t%s" %( setting_value.name, value, value_desc, control_desc )

				else:
					if output_mode == 0:
						print "Value: %s" %( setting_value.name )

			print ""

def PrintLockdownKey( regf_file, lockdown_key_path ):
	lockdown_key = regf_file.get_key_by_path( lockdown_key_path )

	if lockdown_key:
		print "Key: %s" %( lockdown_key_path )
		print ""

		program_name = "iexplore.exe"
		program_value = lockdown_key.get_value_by_name( program_name )

		if program_value:
			value = program_value.get_data_as_integer()
		else:
			value = 0

		if value == 1:
			print "Local Machine lockdown for %s: True" % ( program_name )
		else:
			print "Local Machine lockdown for %s: False" % ( program_name )
		print ""

def Main( argc, argv ):
	if argc != 2:
		PrintUsage()
		return( 1 )

	output_mode = 1

	regf_file = pyregf.file()
	regf_file.open( argv[ 1 ] )

	# HKCU

	PrintLockdownKey(
	 regf_file,
	 "Software\\Policies\\Microsoft\\Internet Explorer\\Main\\FeatureControl\\FEATURE_LOCALMACHINE_LOCKDOWN" )

	PrintLockdownKey(
	 regf_file,
	 "Software\\Microsoft\\Internet Explorer\\Main\\FeatureControl\\FEATURE_LOCALMACHINE_LOCKDOWN" )

	# HKLM

	PrintLockdownKey(
	 regf_file,
	 "Policies\\Microsoft\\Internet Explorer\\Main\\FeatureControl\\FEATURE_LOCALMACHINE_LOCKDOWN" )

	PrintLockdownKey(
	 regf_file,
	 "Microsoft\\Internet Explorer\\Main\\FeatureControl\\FEATURE_LOCALMACHINE_LOCKDOWN" )

	# HKLM Wow64

	PrintLockdownKey(
	 regf_file,
	 "Wow6432Node\\Policies\\Microsoft\\Internet Explorer\\Main\\FeatureControl\\FEATURE_LOCALMACHINE_LOCKDOWN" )

	PrintLockdownKey(
	 regf_file,
	 "Wow6432Node\\Microsoft\\Internet Explorer\\Main\\FeatureControl\\FEATURE_LOCALMACHINE_LOCKDOWN" )

	# TODO: check for value Policies\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\\Security_HKEY_LOCAL_MACHINE_only and its data
	# if not exists or 0, not enabled if 1 only HKLM policy applies

	# HKCU

	PrintZonesKey(
	 regf_file,
	 "Software\\Policies\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\\Zones",
	 output_mode )

	PrintZonesKey(
	 regf_file,
	 "Software\\Policies\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\\Lockdown_Zones",
	 output_mode )

	PrintZonesKey(
	 regf_file,
	 "Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\\Zones",
	 output_mode )

	PrintZonesKey(
	 regf_file,
	 "Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\\Lockdown_Zones",
	 output_mode )

	# HKLM

	PrintZonesKey(
	 regf_file,
	 "Policies\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\\Zones",
	 output_mode )

	PrintZonesKey(
	 regf_file,
	 "Policies\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\\Lockdown_Zones",
	 output_mode )

	PrintZonesKey(
	 regf_file,
	 "Microsoft\\Windows\\CurrentVersion\\Internet Settings\\Zones",
	 output_mode )

	PrintZonesKey(
	 regf_file,
	 "Microsoft\\Windows\\CurrentVersion\\Internet Settings\\Lockdown_Zones",
	 output_mode )

	# HKLM Wow64

	PrintZonesKey(
	 regf_file,
	 "Wow6432Node\\Policies\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\\Zones",
	 output_mode )

	PrintZonesKey(
	 regf_file,
	 "Wow6432Node\\Policies\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\\Lockdown_Zones",
	 output_mode )

	PrintZonesKey(
	 regf_file,
	 "Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\\Zones",
	 output_mode )

	PrintZonesKey(
	 regf_file,
	 "Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\\Lockdown_Zones",
	 output_mode )

	regf_file.close()

	return( 0 )

if __name__ == '__main__':
	sys.exit( Main( len( sys.argv ), sys.argv ) )

