#!/bin/sh

uartsel mc
mc1322x-load -f /tmp/border-router_econotag.bin -t /dev/ttyS0 -r none -c 'mcreset'
