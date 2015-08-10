#!/bin/bash -e

. utils/functions

LAYER=$1
BASE=${LAYER%:*}

utils/addlayer.sh build/$BASE.qcow2 layers/$LAYER tmp/$LAYER.qcow2

mv tmp/$LAYER.qcow2 build/$LAYER.qcow2
