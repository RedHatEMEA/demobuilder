#!/bin/bash -e

. utils/functions

start() {
  apiserver_start
}

stop() {
  apiserver_stop
}

install_layer() {
  echo "Building $1..."

  if [ -d layers/$1 ]; then
    if [ -x layers/$1/install ]; then
      layers/$1/install
    else
      utils/install-layer.sh $1
    fi

  else
    targets/${1##*:}/install ${1%:*}
  fi
}

utils/init.sh

trap stop EXIT
start

if [ $# -eq 0 ]; then
  echo "Usage: $0 layer[:target]"
  echo
  echo "Valid layers:"
  ls layers | grep -v \@ | sed -e 's/^/  /'
  echo
  echo "Valid targets:"
  ls targets | sed -e 's/^/  /'
  echo

else
  install_layer $1
fi

echo "$0: Done."
