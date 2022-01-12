#!/bin/sh
rootdir=tftproot/

mkdir -p $rootdir
echo "Starting tftpd serving $rootdir"
in.tftpd -L --address 10.0.0.1 -s $rootdir
echo $?
