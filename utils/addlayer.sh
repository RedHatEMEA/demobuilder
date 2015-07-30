#!/bin/bash -e

. utils/functions

if [ $# -ne 3 ]; then
  echo "usage: $0 base layer target"
  exit 1
fi

BASE=$1
LAYER=$2
TARGET=$3

utils/createsnap.sh $BASE $TARGET

eval $(utils/run.sh $TARGET)

echo $IP

RSYNC_RSH=utils/ssh.sh rsync -rL $LAYER/@target/ config utils/vm-functions root@$IP:demobuilder
if ! utils/ssh.sh root@$IP "setenforce 0; cd demobuilder; APILISTENER=$APILISTENER LAYER=${LAYER//layers\//} ./install || kill -9 \$\$; cd; rm -rf demobuilder; ( sleep 1; poweroff) &" </dev/null; then
  kill $QEMUPID
  wait_pid $QEMUPID
  exit 1
fi

wait_pid $QEMUPID
