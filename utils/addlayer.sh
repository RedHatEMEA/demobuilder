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
if [ -z "$IP" ]; then
  exit 1
fi

echo $IP

RSYNC_RSH=utils/ssh.sh rsync -rL $LAYER/@target/ utils/{install_wrapper,vm-functions} root@$IP:demobuilder
if [ -e $LAYER/@docs ]; then
  RSYNC_RSH=utils/ssh.sh rsync -rL $LAYER/@docs/* root@$IP:/usr/share/doc/demobuilder
fi

if ! utils/ssh.sh root@$IP "APILISTENER=$APILISTENER LAYER=${LAYER//layers\//} DEBUG=$DEBUG demobuilder/install_wrapper" </dev/null; then
  kill $QEMUPID
  wait_pid $QEMUPID
  exit 1
fi

wait_pid $QEMUPID
