#!/bin/bash -e

. utils/functions

LAYER=$(dirname $0)

TARGET=${LAYER#*/}
BASE=${TARGET%/*}
TARGET=${TARGET//\//:}
BASE=${BASE//\//:}
if [ -e build/$TARGET.qcow2 ]; then
  echo "$0: build/$TARGET.qcow2 already exists, not rebuilding"
  exit
fi

utils/createsnap.sh build/$BASE.qcow2 tmp/$TARGET.qcow2

eval $(utils/run.sh tmp/$TARGET.qcow2)

echo $IP

RSYNC_RSH=utils/ssh.sh rsync -rL $LAYER/@target/ root@$IP:demobuilder
if ! utils/ssh.sh root@$IP "cd demobuilder; chcon system_u:object_r:rpm_exec_t:s0 install; http_proxy=http://$PROXYLISTENER/ ./install || kill -9 \$\$; cd; rm -rf demobuilder; ( sleep 1; poweroff) &" </dev/null; then
  kill $QEMUPID
  wait_pid $QEMUPID
  exit 1
fi

wait_pid $QEMUPID
mv tmp/$TARGET.qcow2 build/$TARGET.qcow2
