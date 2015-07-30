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

  if [[ $1 =~ : ]]; then
    utils/install-layer.sh $1
  else
    layers/$1/install
  fi

  if [ "$2" = "-a" ]; then
    for TARGET in $(ls targets); do
      targets/$TARGET/install $1
    done

  elif [ $# -eq 2 ]; then
    targets/$2/install $1
  fi
}

utils/init.sh

trap stop ERR
start

if [ $# -eq 0 ]; then
  echo "Usage: $0 layer|-a [target|-a]"
  echo
  echo "Valid layers:"
  ls layers | grep -v \@ | sed -e 's/^/  /'
  echo
  echo "Valid targets:"
  ls targets | sed -e 's/^/  /'
  echo

elif [ $1 = "-a" ]; then
  for i in $( ls layers | grep -v \@ ); do
    install_layer $i $2
  done

else
  install_layer $1 $2
fi

stop

echo "Done."
