#!/bin/bash -e

. utils/functions

mkdir -p build keys releases tmp

if [ ! -e keys/demobuilder ]; then
  ssh-keygen -f keys/demobuilder -N ""
fi

if [ ! -e config ]; then
  cp config.example config
fi

if [ ! -e properties ]; then
  cp properties.example properties
fi
