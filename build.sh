#!/bin/bash -e

. utils/functions

start() {
  dcserver_start
  httpserver_start
}

stop() {
  dcserver_stop
  httpserver_stop
}

install_layer() {
  echo "Building $1..."

  LAYER=${1//:/\/}
  layers/$LAYER/install

  if [ "$2" = "-a" ]; then
    for TARGET in $(ls targets); do
      targets/$TARGET/install $LAYER
    done

  elif [ $# -eq 2 ]; then
    targets/$2/install $LAYER
  fi
}

utils/init.sh

trap stop ERR
start

if [ $# -eq 0 ]; then
  echo "Usage: $0 layer|-a [target|-a]"
  echo
  echo "Valid layers:"
  ( cd layers && find * -type d -not -name '@*' | sort | sed -e 's!/!:!g' ) | sed -e 's/^/  /'
  echo
  echo "Valid targets:"
  ls targets | sed -e 's/^/  /'
  echo

elif [ $1 = "-a" ]; then
  for i in $( cd layers && find * -type d -not -name '@*' | sort | sed -e 's!/!:!g' ); do
    install_layer $i $2
  done

else
  install_layer $1 $2
fi

stop

echo "Done."