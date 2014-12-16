#!/bin/bash -e

. utils/functions

if [ $# -lt 1 -o $# -gt 2 ]; then
  echo "usage: $0 base [path/to/layer]"
  exit 1
fi

LAYER=${2:-$(dirname $0)}

TARGET=$1:$(basename $LAYER)
if [ -e build/$TARGET.qcow2 ]; then
  echo "$0: build/$TARGET.qcow2 already exists, not rebuilding"
  exit
fi

utils/createsnap.sh build/$1.qcow2 tmp/$TARGET.qcow2

eval $(utils/run.sh tmp/$TARGET.qcow2)

echo $IP

RSYNC_RSH=utils/ssh.sh rsync -rL $LAYER/target/ root@$IP:demobuilder
utils/ssh.sh root@$IP "cd demobuilder; http_proxy=http://$PROXYLISTENER/ ./install; cd; rm -rf demobuilder; rm /etc/udev/rules.d/70-persistent-net.rules; ( sleep 1; poweroff) &" </dev/null

wait_pid $QEMUPID

mv tmp/$TARGET.qcow2 build/$TARGET.qcow2
