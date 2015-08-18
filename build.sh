#!/bin/bash -e

utils/init.sh

. utils/functions

if [ $# -eq 0 ]; then
  echo "Usage: $0 layer[:target]..."
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

  for item in "$@"; do
    echo "Building $item..."

    if [ -d layers/$item ]; then
      if [ -x layers/$item/install ]; then
        layers/$item/install
      else
        utils/install-layer.sh $item
      fi

    else
      targets/${item##*:}/install ${item%:*}
    fi

    echo "$0: Done building $item."
  done
fi
