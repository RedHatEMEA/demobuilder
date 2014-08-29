#!/bin/bash

ROOT=$(realpath ../..)
. $ROOT/config
. $ROOT/utils/functions

mkbuild

$ROOT/utils/createsnap.sh $ROOT/demos/gui/build/gui.qcow2 build/openshift-uncompressed.qcow2

eval $($ROOT/utils/run.sh build/openshift-uncompressed.qcow2)

echo $IP

RSYNC_RSH=../../utils/ssh.sh rsync -rL vm-scripts/* root@$IP:
../../utils/ssh.sh root@$IP ./install.sh 

exit

while [ -e /proc/$QEMUPID ]; do
  sleep 1
done

qemu-img convert -p -O qcow2 -o backing_file=$ROOT/base/rhel-server-6.5/build/rhel-server-6.5.qcow2 build/openshift-uncompressed.qcow2 build/openshift.qcow2

rm build/openshift-uncompressed.qcow2
