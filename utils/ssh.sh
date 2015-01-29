#!/bin/bash -e

. utils/functions

exec ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=QUIET -i keys/demobuilder "$@"
