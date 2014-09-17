#!/bin/bash -e

cleanup() {
  trap INT
  kill -2 $$
}

trap cleanup INT

qemu-kvm "$@"
