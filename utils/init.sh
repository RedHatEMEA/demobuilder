#!/bin/bash -e

. utils/functions

mkdir -p build keys tmp

if [ ! -e keys/demobuilder ]; then
  ssh-keygen -f keys/demobuilder -N ""
fi
