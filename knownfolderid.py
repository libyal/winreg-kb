#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Script to print the known folder identifiers (KNOWNFOLDERID)
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
	print "Usage: ./knownfolderid.py registry_file"
	print ""
	print "   	registry_file: The path of the SOFTWARE registry file."
	print ""

def Main( argc, argv ):
	if argc != 2:
		PrintUsage()
		return( 1 )

	folder_descriptions_key_path = "Microsoft\\Windows\\CurrentVersion\\Explorer\\FolderDescriptions"

	regf_file = pyregf.file()
	regf_file.open( argv[ 1 ] )

	folder_descriptions_key = regf_file.get_key_by_path( folder_descriptions_key_path )

	if folder_descriptions_key:
		for known_folder_key in folder_descriptions_key.sub_keys:
			guid = known_folder_key.name.lower()

			value = known_folder_key.get_value_by_name( "Name" )
			if value:
				name = value.get_data_as_string()
			else:
				name = ""

			value = known_folder_key.get_value_by_name( "LocalizedName" )
			if value:
				localized_name = value.get_data_as_string()
			else:
				localized_name = ""

			print "%s\t%s\t%s" %( guid, name, localized_name )
	else:
		print "No folder descriptions key found."

	regf_file.close()

	return( 0 )

if __name__ == '__main__':
	sys.exit( Main( len( sys.argv ), sys.argv ) )

