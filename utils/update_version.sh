#!/bin/bash
# Script to update the version information.

DATE_VERSION=`date +"%Y%m%d"`;
DATE_DPKG=`date -R`;
EMAIL_DPKG="Joachim Metz <joachim.metz@gmail.com>";

sed -i -e "s/^\(__version__ = \)'[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'$/\1'${DATE_VERSION}'/" winregrc/__init__.py
sed -i -e "s/^\(winreg-kb \)([0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]-1)/\1(${DATE_VERSION}-1)/" config/dpkg/changelog
sed -i -e "s/^\( -- ${EMAIL_DPKG}  \).*$/\1${DATE_DPKG}/" config/dpkg/changelog
