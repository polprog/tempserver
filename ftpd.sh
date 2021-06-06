#!/bin/sh
# Note: bftpd is very, very stupid, and it *will* serve your / directory
# (as root) if it cannot chroot. Furthermore, the paths in the configuration
# file are interpreted absolute. To circumvent this, we create a temporary
# config file with the right, absolute paths. This will fail if you have
# comma in your file path. 

bftpd=/usr/sbin/bftpd

clean() {
    echo -n "Cleaning up..."
    rm -f bftpd_$$.conf
    echo "done."
}
    
trap clean INT

mkdir -p ftproot/
sed -e "s,%PWD%,$('pwd'),g" < bftpd.conf > bftpd_$$.conf

$bftpd -D -c ./bftpd_$$.conf
