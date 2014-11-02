#!/bin/sh
BLASTER_DEVICE=/dev/lirc1
killall lircd
killall eventlircd
nohup python /storage/.config/lircsocket.py -e /run/lirc/eventlircd -l /run/lirc/lircd0 -s /run/lirc/lircd >/dev/null &
ir-keytable -p NEC -p RC-6 -p LIRC
nohup /usr/sbin/eventlircd -f --evmap=/etc/eventlircd.d --socket=/run/lirc/eventlircd --release=_UP >/dev/null &
/usr/sbin/lircd --driver=default --device=${BLASTER_DEVICE} --output=/run/lirc/lircd0 --pidfile=/run/lirc/lircd0.pid /storage/.config/lircd.conf
(while sleep 1; do nohup irexec /storage/.config/irexec.conf >/dev/null;done) &
disown
