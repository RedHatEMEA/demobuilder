#!/bin/bash -e

. utils/functions

build() {
  utils/builddeps.py $1 | while read LAYER BASE; do
    if [ -n "$BASE" ]; then
      echo Building $BASE:$LAYER...
    else
      echo Building $LAYER...
    fi
    layers/$LAYER/install $BASE
  done
}

cleanup() {
  proxy_stop
  httpserver_stop
}

utils/init.sh

trap cleanup 0
proxy_start
httpserver_start

if [ $# -eq 0 ]; then
  for i in targets/*; do
    build $(basename $i)
  done
else
  build $1
fi
