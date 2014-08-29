#!/bin/bash

if ! [ -e $1 ] || [ -e $2 ]; then
  echo bad
  exit 1
fi

qemu-img create -f qcow2 -o backing_file=$1 $2
