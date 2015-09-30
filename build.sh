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
    echo "Building layers $item..."
    layers=$item
    parentLayer=${layers%%:*}
    continue=true
    
    while [ continue ]; do 
      echo "Checking $parentLayer exists..."     
      if ! [[ -a build/$parentLayer.qcow2 ]]; then
        echo "Need to build $parentLayer first"
          if [ -d layers/$parentLayer ]; then
      if [ -x layers/$parentLayer/install ]; then
        layers/$parentLayer/install
      else
        utils/install-layer.sh $parentLayer
      fi
    else
      targets/${parentLayer##*:}/install ${parentLayer%:*}
    fi
      else
        echo "$parentLayer already built, moving onto next"
      fi      
      
      if [[ $layers == *":"* ]]; then
        #echo "more layers to process"
        layers=${item/$parentLayer:/""}
        parentLayer=$parentLayer:${layers%%:*}
      else
        #echo "no more layers"
        let continue=false
      fi
    done
    

    echo "$0: Done building $item."
  done
fi