#!/bin/bash
# Temporary DHCP server script
# http://polprog.net 2019
# 3-clause BSD licence

serverip=10.0.0.1/24
iface=enp0s25
dhcpflags="-4 -d -cf dhcpd.conf"

function quit(){
    echo -ne "\nCleaning up..."
    ip a del $serverip dev $iface
    echo "done."
}

trap quit INT
echo "Starting standalone DHCP server on $iface"
echo "Server IP is $serverip"
echo "Setting a static address..."
ip a add $serverip dev $iface
echo "Starting the server..."
dhcpd $dhcpflags $iface
