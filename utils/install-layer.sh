#!/bin/bash -e

. utils/functions

LAYER=$1
BASE=${LAYER%:*}

if [ -e build/$LAYER.qcow2 ]; then
  echo "$0: build/$LAYER.qcow2 already exists, not rebuilding"
  exit
fi

utils/addlayer.sh build/$BASE.qcow2 layers/$LAYER tmp/$LAYER.qcow2

mv tmp/$LAYER.qcow2 build/$LAYER.qcow2
