#!/bin/bash

MACADDR=$(ifconfig eth0 | awk '/ether / { print $2 }')

sed -i -e '/^MACADDR=/ d' /etc/sysconfig/network-scripts/ifcfg-br-ex
echo MACADDR=$MACADDR >>/etc/sysconfig/network-scripts/ifcfg-br-ex
