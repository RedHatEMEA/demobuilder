#!/bin/bash -e

. utils/functions

for pkg in git libcdio libguestfs libvirt pigz pyOpenSSL python-bottle PyYAML qemu-kvm; do
  rpm -q $pkg &>/dev/null || echo "WARNING: please install $pkg."
done

for proc in libvirtd; do
  pidof $proc &>/dev/null || echo "WARNING: please start $proc."
done

sudo iptables -C INPUT_ZONES -i $BUILD_BRIDGE -j IN_trusted &>/dev/null || echo "WARNING: please verify firewall configuration."

mkdir -p build isos keys releases tmp

if [ ! -e keys/demobuilder ]; then
  ssh-keygen -f keys/demobuilder -N ""
fi

if [ ! -e config.yml ]; then
  cp config.yml.example config.yml
fi
