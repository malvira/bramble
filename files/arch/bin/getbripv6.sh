#!/bin/sh
#set -x

IPV6=`ip -o -f inet6 addr show tun scope global | tr -s ' ' ' ' | cut -d ' ' -f 4 | cut -d '/' -f 1`
NEWIP=`ipv6calc $IPV6 --addr2uncompaddr | cut -d ':' -f 1-7`:2

echo $NEWIP
