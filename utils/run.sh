#!/bin/bash -e

. utils/functions

if [ $# -eq 0 ]; then
  echo "usage: $0 snap"
  exit 1
fi

stop() {
  rm -rf $TMPDIR
}

trap stop EXIT
TMPDIR=$(mktemp -d)
VNC=${VNC:-:0}

utils/sigwrap /usr/bin/qemu-kvm -nodefaults \
  -cpu host \
  -smp $BUILD_CPUS \
  -m $BUILD_MEM \
  -drive discard=unmap,file=$1,id=disk1,if=none,cache=unsafe \
  -device virtio-scsi-pci \
  -device scsi-disk,drive=disk1 \
  -netdev bridge,id=net0,br=$BUILD_BRIDGE \
  -device virtio-net-pci,netdev=net0,mac=$(utils/random-mac.py) \
  -chardev socket,id=chan0,path=$TMPDIR/rhev.sock,server,nowait \
  -chardev socket,id=chan1,path=$TMPDIR/qemu.sock,server,nowait \
  -device virtio-serial-pci \
  -device virtserialport,chardev=chan0,name=com.redhat.rhevm.vdsm \
  -device virtserialport,chardev=chan1,name=org.qemu.guest_agent.0 \
  -device vmware-svga \
  -vnc $VNC \
  -usbdevice tablet \
  &>/dev/null &

QEMUPID=$!
echo QEMUPID=$QEMUPID

utils/wait-ip.py $TMPDIR $QEMUPID
