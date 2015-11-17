#!/bin/bash -e

. utils/functions

LAYER=$1
BASE=${LAYER%:*}

if ! needs_build build/$LAYER.qcow2 layers/$LAYER build/$BASE.qcow2; then
  exit 0
fi

utils/addlayer.sh build/$BASE.qcow2 layers/$LAYER tmp/$LAYER.qcow2

mv tmp/$LAYER.qcow2 build/$LAYER.qcow2
