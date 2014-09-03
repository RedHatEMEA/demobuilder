#!/bin/bash -e

. utils/functions

build() {
  echo Building $1...
  layers/$1/install $2
}

mkdir -p build keys
[ -e keys/demobuilder ] || ssh-keygen -f keys/demobuilder -N ""

proxy_start
httpserver_start

if [ $# -eq 0 ]; then
  utils/builddeps.py <buildlist | while read LAYER BASE; do
    build $LAYER $BASE
  done
else
  echo $1 | utils/builddeps.py | while read LAYER BASE; do
    build $LAYER $BASE
  done
fi

proxy_stop
httpserver_stop
