#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Script to print the shell folder class identifiers
# from the SOFTWARE Registry file (REGF)
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

def PrintUsage():
	print "Usage: ./shellfolders.py registry_file"
	print ""
	print "   	registry_file: The path of the SOFTWARE registry file."
	print ""

def Main( argc, argv ):
	if argc != 2:
		PrintUsage()
		return( 1 )

	class_identifiers_key_path = "Classes\\CLSID"

	regf_file = pyregf.file()
	regf_file.open( argv[1] )

	class_identifiers_key = regf_file.get_key_by_path( class_identifiers_key_path )

	if class_identifiers_key:
		for class_identifier_key in class_identifiers_key.sub_keys:
			guid = class_identifier_key.name.lower()

			shell_folder_key = class_identifier_key.get_sub_key_by_name( "ShellFolder" )
			if shell_folder_key:
				value = class_identifier_key.get_value_by_name( "" )
				if value:
					# The value data type does not have to be a string there try to
					# decode the data as an UTF-16 little-endian string and strip
					# the trailing end-of-string character
					name = value.data.decode("utf-16-le")[:-1]
				else:
					name = ""

				value = class_identifier_key.get_value_by_name( "LocalizedString" )
				if value:
					# The value data type does not have to be a string there try to
					# decode the data as an UTF-16 little-endian string and strip
					# the trailing end-of-string character
					localized_string = value.data.decode("utf-16-le")[:-1]
				else:
					localized_string = ""

				print "%s\t%s\t%s" %( guid, name, localized_string )
	else:
		print "No class identifiers key found."

	regf_file.close()

	return( 0 )

if __name__ == '__main__':
	sys.exit( Main( len( sys.argv ), sys.argv ) )

