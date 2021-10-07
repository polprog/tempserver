#!/bin/bash
# Temporary SSH server script
# http://polprog.net 2021
# 3-clause BSD licence


keyfile="klucz.key"
address="localhost:2222"
options="-w"

if [ $EUID -ne 0 ]; then echo "This script must be run as root!"; exit 1; fi
if ! which dropbear || ! which dropbearkey; then
    echo "dropbear not found in PATH!";
    exit 1;
fi

[ -f $keyfile ] || dropbearkey -t ecdsa -f $keyfile


echo "Starting dropbear SSH server..."
dropbear -r $keyfile -p $address -FER $options

#TODO: check if dropbear can be made to run as regular user, allowing to log in only to the user who ran it. 
