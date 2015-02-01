#!/bin/bash -e

. utils/vm-functions

find -L cache -name repodata -type d | xargs rm -rf
