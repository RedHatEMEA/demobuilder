#!/bin/bash -e

. utils/functions

if [ -z "$PROXYLISTENER" -o -z "$BRIDGE" -o ! -e keys/demobuilder ]; then
  echo "$0: build environment incorrect"
  exit 1
fi

if [ $# -lt 1 -o $# -gt 2 ]; then
  echo "usage: $0 base [path/to/layer]"
  exit 1
fi

LAYER=${2:-$(dirname $0)}

TARGET=build/$1:$(basename $LAYER).qcow2
if [ -e $TARGET ]; then
  echo "$0: $TARGET already exists, not rebuilding"
  exit
fi

utils/createsnap.sh build/$1.qcow2 $TARGET

eval $(utils/run.sh $TARGET)

echo $IP

RSYNC_RSH=utils/ssh.sh rsync -rL $LAYER/target/ root@$IP:demobuilder
utils/ssh.sh root@$IP "cd demobuilder; http_proxy=http://$PROXYLISTENER/ ./install; cd; rm -rf demobuilder; rm /etc/udev/rules.d/70-persistent-net.rules; poweroff"

wait_pid $QEMUPID

compress_qcow2 $TARGET
