#!/bin/bash -e

. utils/functions

if [ $# -ne 2 -o ! -e "$(realpath $1)" ]; then
  echo "usage: $0 base snap"
  exit 1
fi

qemu-img create -q -f qcow2 -o backing_file=$(realpath $1) $2
