#!/bin/sh
set -x
IPV6=`ip -f inet6 addr show tun scope global | grep "inet6 2002:" | tr -s ' ' ' ' | cut -d ' ' -f 3 | cut -d '/' -f 1`
NEWIP=`ipv6calc $IPV6 --addr2uncompaddr | cut -d ':' -f 1-7`:2

mc1322x-load.pl -r none -a 0 -b 0 -e -f /var/cache/bradmin/br.bin -t /dev/ttyS0 -c 'mcreset'
#tunslip6 -s /dev/ttyS0 2002:3239:614b:a::2/64 -v3 -t tunbr
tunslip6 -v3 -s /dev/ttyS0 -t tunbr $NEWIP/64 &> /var/log/bradmin/tunslip6.log &
