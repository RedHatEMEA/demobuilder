#!/bin/bash -x

qemu-img info --backing-chain $1
