#!/bin/bash -e

. utils/functions

utils/init.sh

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
  trap apiserver_stop EXIT
  apiserver_start

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

  echo "$0: Done."
fi
