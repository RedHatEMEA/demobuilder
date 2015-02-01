#!/bin/bash -e

. utils/functions

LAYER=$(echo $0 | sed -e 's!^[^/]*/!!; s!/[^/]*$!!')
BASE=${LAYER%/*}
BASE=${BASE//\//:}
TARGET=${LAYER//\//:}

if [ -e build/$TARGET.qcow2 ]; then
  echo "$0: build/$TARGET.qcow2 already exists, not rebuilding"
  exit
fi

utils/addlayer.sh build/$BASE.qcow2 layers/$LAYER tmp/$TARGET.qcow2

mv tmp/$TARGET.qcow2 build/$TARGET.qcow2
