#!/bin/bash -e

qemu-img convert -cp -O qcow2 $1 $1-tmp
mv $1-tmp $1
