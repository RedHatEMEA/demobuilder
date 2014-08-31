#!/bin/bash -x

. utils/functions

base() {
  [ -e build/$1.qcow2 ] || base/$1/install
}

layer() {
  [ -e build/$3.qcow2 ] || utils/addlayer.sh build/$1.qcow2 layers/$2 build/$3.qcow2
}

target() {
  layer $1 $2 $1-$2
  [ -e build/$3 ] || targets/$2/install build/$1-$2.qcow2 build/$3
}

mkdir -p build

proxy_start
httpserver_start

base rhel-server-6.5
base rhel-guest-image-6.5

layer rhel-server-6.5 gui rhel-server-6.5-gui
layer rhel-server-6.5-gui openshift rhel-server-6.5-gui-openshift

target rhel-server-6.5 vagrant rhel-server-6.5-vagrant.box

proxy_stop
httpserver_stop
