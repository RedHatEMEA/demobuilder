#!/bin/bash -e

. utils/functions

mkdir -p build keys tmp
[ -e keys/demobuilder ] || ssh-keygen -f keys/demobuilder -N ""
