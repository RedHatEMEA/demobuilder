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
    currentLayer=${item%%:*}
    remainingLayers=${item#*:}

    while true; do
      echo "$0: Building $currentLayer..."
      if [ -d layers/$currentLayer ]; then
        if [ -x layers/$currentLayer/install ]; then
          layers/$currentLayer/install
        else
          utils/install-layer.sh $currentLayer
        fi
      else
        targets/${currentLayer##*:}/install ${currentLayer%:*}
      fi
      echo "$0: Done building $currentLayer."

      if [[ "$currentLayer" == "$item" ]]; then
        break
      fi

      currentLayer=$currentLayer:${remainingLayers%%:*}
      remainingLayers=${remainingLayers#*:}
    done
  done
fi
