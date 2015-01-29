#!/bin/bash -e

. utils/functions

start() {
  proxy_start
  httpserver_start
}

stop() {
  proxy_stop
  httpserver_stop
}

utils/init.sh

trap stop ERR
start

if [ $# -eq 0 ]; then
  echo "Usage: $0 -a"
  echo "       $0 target"
  echo
  echo "Valid targets:"
  ( cd layers && find * -type d -not -name '@*' | sort ) | sed -e 's/^/  /'
  echo
elif [ $1 = "-a" ]; then
  for i in $( cd layers && find * -type d -not -name '@*' | sort ); do
    layers/$i/install
  done
else
  layers/$1/install
fi

stop
