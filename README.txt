
      .'\.         Temporary  
    .'   \'.	   Eephemeral 
   /\'.   \ '.	   Networking 
  / |\ '.  \  'x   Toolkit    
 /  |\\  ','
/__/  |\,' 'x
          
          

Polprog's TENT
===============

TENT (Temporary Ephemeral Networking Toolkit) is is a collection of scripts that
allow you to set up a temporary DHCP, FTP and TFTP server. The aim of this is to
enable creating a fast test network on a computer without the hassle of needing
to edit system-wide configuration files or enable/disable system services.

Current services
-----------------

TENT v1.0 supports setting up the following services:

    - DHCP
    - FTP
    - TFTP

DHCP and TFTP services allow you to set up a PXE server, see the "PXE server"
section below.

Dependencies
-------------
The DHCP server uses ip(8) and dhcpd(8). This was tested on Debian 10 with
isc-dhcp-server as dhcpd.

The FTP server uses bftpd. bftpd is not available in Debian repositories, you
will have to build it from source. It is available in Arch linux. 

The TFTP server uses the HPA tftpd. It is available in the tftpd-hpa package on
debian.

Please note, that if you are installing these from the repository, you
will most likely have to stop and disable the system services, as they are
enabled during install by default. Leaving a DHCP/TFTP that starts on boot may
cause an unpleasant surprise when troubleshooting network issues later (who
wants to accidentally have a second DHCP server to a network?)

Usage
------
Each of the servers has a wrapper script. These scripts do not take any
arguments. Usually it is enough to run the script as root. These scripts can be
run as background jobs. Each script has got a set of user-configurable
variables, and, if necesary, a similarly named configuration file.

For example, to run the dhcp server, one would adjust the variables in dhcpd.sh
and the settings in dhcpd.conf to match, and issue a command:

$ sudo ./dhcpd.sh
or
# ./dhcpd.sh

All scripts can be stopped with ^C, scripts that need cleanup trap SIGINT as
needed.

PXE server
-----------
For a PXE server you will want to put a PXE bootloader in the tftproot
directory, and adjust the filename stanza in dhcpd.conf. The default filename in
dhcpd.conf is set for PXELINUX bootloader. For a minimal PXELINUX setup, place
the following files from the PXELINUX distribution in tftproot directory:

chain.c32
libcom32.c32
memdisk
pxelinux.0  
ldlinux.c32
libutil.c32
menu.c32

And place the SYSLINUX configuration file in:
tftproot/pxelinux.cfg/default

More information can be found on the SYSLINUX wiki.


Files
-----

dhcpd.sh    - DHCP server script
dhcpd.conf  - DHCP server configuration file

ftpd.sh     - FTP server script
bftpd.conf  - FTP server config file

tftpd.sh    - TFTP server script
tftproot/   - root directory of TFTP server
troubleshooting.txt  - troubleshooting the TFTP server

forward.sh  - Utility script to enable NAT for the DHCP server.


