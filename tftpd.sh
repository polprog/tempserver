#!/bin/sh
echo "Starting tftpd serving tftproot/"
in.tftpd -L --address 10.0.0.1 -s tftproot/
