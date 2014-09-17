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

utils/init.sh

proxy_start
httpserver_start

if [ $# -eq 0 ]; then
  echo "Usage: $0 -a"
  echo "       $0 target"
  echo
  echo "Valid targets:"
  ls targets | sed -e 's/^/  /'
  echo
elif [ $1 = "-a" ]; then
  for i in targets/*; do
    build $(basename $i)
  done
else
  build $1
fi

proxy_stop
httpserver_stop
