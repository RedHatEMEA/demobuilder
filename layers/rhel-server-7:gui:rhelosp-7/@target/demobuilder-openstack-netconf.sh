#!/bin/bash

. /root/keystonerc_admin

IP=$(ip addr show dev br-ex | awk '/inet / { print $2; }')
GW=$(route -n | awk '/^0\.0\.0\.0 / { print $2 }')
DNS=$(awk '/^nameserver / { print $2; exit }' </etc/resolv.conf)
eval $(ipcalc -np $IP)

TENANT=$(keystone tenant-get demo | awk '$2 == "id" { print $4 }')

neutron router-gateway-clear router1
for int in $(neutron router-port-list -F fixed_ips router1 -f csv | sed 1d | cut -d'"' -f8); do
  neutron router-interface-delete router1 $int
done
neutron router-delete router1
neutron subnet-delete public_subnet
neutron subnet-delete private_subnet
neutron net-delete public
neutron net-delete private

neutron net-create public --router:external=True
neutron net-create private --tenant-id $TENANT

neutron subnet-create --name public_subnet --enable_dhcp=False --gateway=$GW public $NETWORK/$PREFIX
neutron subnet-create --name private_subnet --tenant-id $TENANT private 10.0.0.0/24 --dns-nameserver $DNS

neutron router-create --tenant-id $TENANT router1
neutron router-gateway-set router1 public
neutron router-interface-add router1 private_subnet
