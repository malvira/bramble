#/bin/busybox

GPIO=453

if [ ! -d /sys/class/gpio/gpio$GPIO ]
then
	busybox echo $GPIO > /sys/class/gpio/export
	busybox echo "out" > /sys/class/gpio/gpio$GPIO/direction
fi

while /bin/true; do 
	busybox echo 0 > /sys/class/gpio/gpio$GPIO/value
	busybox sleep 1
	busybox echo 1 > /sys/class/gpio/gpio$GPIO/value
	busybox sleep 1
done
