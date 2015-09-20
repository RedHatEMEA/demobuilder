#!/bin/bash -e

if [ ! -e config.yml ]; then
  cp config.yml.example config.yml
fi

. utils/functions

FATAL=0

for pkg in git libcdio libguestfs libvirt pigz pyOpenSSL python-apsw python-bottle python-cherrypy PyYAML qemu-kvm sqlite; do
  if ! rpm -q $pkg &>/dev/null; then
    echo "FATAL: please install $pkg.  You probably need to run:"
    echo "sudo dnf -y install $pkg"
    echo
    FATAL=1
  fi
done

for svc in libvirtd; do
  if ! pidof $svc &>/dev/null; then
    echo "FATAL: please start $svc.  You probably need to run:"
    echo "sudo systemctl enable $svc.service"
    echo "sudo systemctl start $svc.service"
    echo
    FATAL=1
  fi
done

for contrib in contrib/*; do
  if [ ! -e $contrib/.git ] || git submodule status $contrib | grep -qv '^ '; then
    echo "FATAL: please check submodules out correctly.  In the future, use the"
    echo "       --recursive option to git clone / --recurse-submodules option to"
    echo "       git pull.  For now, you probably need to run:"
    echo "git submodule init $contrib"
    echo "git submodule update $contrib"
    echo
    FATAL=1
  fi
done

sudo iptables -C INPUT_ZONES -i $BUILD_BRIDGE -j IN_trusted &>/dev/null || echo "WARNING: please verify firewall configuration."

mkdir -p build isos keys releases tmp

if [ ! -e keys/demobuilder ]; then
  ssh-keygen -f keys/demobuilder -N ""
fi

if [ $FATAL != 0 ]; then
  exit 1
fi
