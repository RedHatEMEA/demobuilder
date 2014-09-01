#!/bin/bash -x

. utils/functions

if [ $# -ne 3 ]; then
  echo "usage: $0 base layer dest"
  exit 1
fi

utils/createsnap.sh $1 $3

eval $(utils/run.sh $3)

echo $IP

RSYNC_RSH=utils/ssh.sh rsync -rL $2/ root@$IP:demobuilder
utils/ssh.sh root@$IP "cd demobuilder; http_proxy=http://$PROXYLISTENER/ ./install; cd; rm -rf demobuilder; rm /etc/udev/rules.d/70-persistent-net.rules; poweroff"

wait_pid $QEMUPID

# compress_qcow2 $3
