#!/bin/busybox sh

GPIO=453

if [ ! -d /sys/class/gpio/gpio$GPIO ]
then
	echo $GPIO > /sys/class/gpio/export
	echo "out" > /sys/class/gpio/gpio$GPIO/direction
fi

while /bin/true; do 
	echo 0 > /sys/class/gpio/gpio$GPIO/value
	sleep 1
	echo 1 > /sys/class/gpio/gpio$GPIO/value
	sleep 1
done
