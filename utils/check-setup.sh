#!/bin/bash

. utils/functions

for pkg in git libcdio libguestfs libvirt pigz pyOpenSSL python-bottle python-yaml qemu-kvm; do
  rpm -q $pkg &>/dev/null || echo "Please install $pkg."
done

for proc in libvirtd; do
  pidof $proc &>/dev/null || echo "Please start $proc."
done

sudo iptables -C INPUT_ZONES -i $BRIDGE -j IN_trusted &>/dev/null || echo "Please verify firewall configuration."
