#!/bin/bash -e

. utils/functions

find -L cache -name repodata -type d | xargs rm -rf
