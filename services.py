#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Script to print the drivers and services from the SYSTEM
# Registry file (REGF)
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

REG_NONE = 0
REG_SZ = 1
REG_EXPAND_SZ = 2
REG_BINARY = 3
REG_DWORD = 4
REG_DWORD_LITTLE_ENDIAN = 4
REG_DWORD_BIG_ENDIAN = 5
REG_LINK = 6
REG_MULTI_SZ = 7
REG_RESOURCE_LIST = 8
REG_FULL_RESOURCE_DESCRIPTOR = 9
REG_RESOURCE_REQUIREMENT_LIST = 10
REG_QWORD = 11

def PrintUsage():
	print "Usage: ./services.py registry_file"
	print ""
	print "   	registry_file: The path of the SYSTEM registry file."
	print ""

def PrintServices( control_set_key ):
	services_key = control_set_key.get_sub_key_by_name( "Services" )

	if services_key:
		print "Control set: {0:s}".format( control_set_key.name )
		print "\tNumber of entries\t: {0:d}".format( services_key.number_of_sub_keys )
		print ""

		for service_key in services_key.sub_keys:
			print "{0:s}".format( service_key.name )

			type_value = service_key.get_value_by_name( "Type" )
			object_name_string = "Object name"

			if type_value:
				type_value = type_value.data_as_integer

				if type_value == 0x00000001:
					type_string = "Kernel device driver"

				elif type_value == 0x00000002:
					type_string = "File system driver"

				elif type_value == 0x00000004:
					type_string = "Adapter arguments"

				elif type_value == 0x00000010:
					type_string = "Stand-alone service"
					object_name_string = "Account name"

				elif type_value == 0x00000020:
					type_string = "Shared service"
					object_name_string = "Account name"

				else:
					if type_value == 0x00000110:
						object_name_string = "Account name"

					type_string = "Unknown 0x{0:08x}".format( type_value )

				print "\tType\t\t\t: {0:s}".format( type_string )

			display_name_value = service_key.get_value_by_name( "DisplayName" ) 

			if display_name_value:
				if ( display_name_value.type == REG_SZ or display_name_value.type == REG_EXPAND_SZ ):
					print "\tDisplay name\t\t: {0:s}".format( display_name_value.data_as_string )

			description_value = service_key.get_value_by_name( "Description" ) 

			if description_value:
				print "\tDescription\t\t: {0:s}".format( description_value.data_as_string )

			image_path_value = service_key.get_value_by_name( "ImagePath" ) 

			if image_path_value:
				print "\tExecutable\t\t: {0:s}".format( image_path_value.data_as_string )

			object_name_value = service_key.get_value_by_name( "ObjectName" ) 

			if object_name_value:
				print "\t{0:s}\t\t: {1:s}".format( object_name_string, object_name_value.data_as_string )

			start_value = service_key.get_value_by_name( "Start" )

			if start_value:
				start_value = start_value.data_as_integer

				if start_value == 0x00000000:
					start_string = "Boot"

				elif start_value == 0x00000001:
					start_string = "System"

				elif start_value == 0x00000002:
					start_string = "Automatic"

				elif start_value == 0x00000003:
					start_string = "On demand"

				elif start_value == 0x00000004:
					start_string = "Disabled"

				else:
					start_string = "Unknown 0x{0:08x}".format( start_value )

				print "\tStart\t\t\t: {0:s}".format( start_string )

			print ""


def Main( argc, argv ):
	if argc != 2:
		PrintUsage()
		return( 1 )

	regf_file = pyregf.file()
	regf_file.open( argv[1] )

	root_key = regf_file.get_root_key()

	if root_key:
		for control_set_key in root_key.sub_keys:
			if control_set_key.name.startswith( "ControlSet" ):
				PrintServices( control_set_key )
	else:
		print "No root key found."

	regf_file.close()

	return( 0 )

if __name__ == '__main__':
	sys.exit( Main( len( sys.argv ), sys.argv ) )

