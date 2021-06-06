#!/bin/sh

IFACE_INT=enp0s25
IFACE_EXT=wls1

if [ $# -lt 1 ]; then
    echo "Usage: $1 [enable|disable]"
    exit 1;
fi

if [ $1 = "enable" ]; then
    echo -n "Enabling IPv4 forwarding from $IFACE_INT to $IFACE_EXT..."
    echo 1 > /proc/sys/net/ipv4/ip_forward
     /sbin/iptables -t nat -A POSTROUTING -o $IFACE_EXT -j MASQUERADE
     /sbin/iptables -A FORWARD -i $IFACE_INT -o $IFACE_EXT -m state \
		    --state RELATED,ESTABLISHED -j ACCEPT
     /sbin/iptables -A FORWARD -i $IFACE_INT -o $IFACE_EXT -j ACCEPT
     echo "done"
fi

if [ $1 = "disable" ]; then
    echo -n "Disabling IPv4 forwarding from $IFACE_INT to $IFACE_EXT..."
    echo 1 > /proc/sys/net/ipv4/ip_forward
    /sbin/iptables -t nat -D POSTROUTING -o $IFACE_EXT -j MASQUERADE
    /sbin/iptables -D FORWARD -i $IFACE_INT -o $IFACE_EXT -m state \
		    --state RELATED,ESTABLISHED -j ACCEPT
    /sbin/iptables -D FORWARD -i $IFACE_INT -o $IFACE_EXT -j ACCEPT
    echo "done"
fi
