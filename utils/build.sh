#!/bin/bash -e

. utils/functions

trap apiserver_stop EXIT
apiserver_start

if [ -d layers/$1 ]; then
  if [ -x layers/$1/install ]; then
    layers/$1/install
  else
    utils/install-layer.sh $1
  fi
else
  targets/${1##*:}/install ${1%:*}
fi
