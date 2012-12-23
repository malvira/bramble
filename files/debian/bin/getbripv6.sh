#!/bin/sh
#set -x

IPV6=`ip -f inet6 addr show tun scope global | grep "inet6 2002:" | tr -s ' ' ' ' | cut -d ' ' -f 3 | cut -d '/' -f 1`
NEWIP=`ipv6calc $IPV6 --addr2uncompaddr | cut -d ':' -f 1-7`:2

echo $NEWIP
