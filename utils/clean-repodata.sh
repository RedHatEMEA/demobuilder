#!/bin/bash -e

. utils/functions

find -L cache -name repodata -type d | xargs rm -rf
rm -rf cache/registry.access.redhat.com:443/v1/repositories cache/registry-1.docker.io:443/v2/*/*/manifests
