#!/bin/bash -e

. utils/functions

TMPDIR=$(mktemp -d)

utils/sigwrap /usr/bin/qemu-kvm -nodefaults \
  -smp 2 \
  -m 2048 \
  -drive discard=unmap,file=$1,id=disk1,if=none \
  -device virtio-scsi-pci \
  -device scsi-disk,drive=disk1 \
  -net bridge,br=virbr0 \
  -net nic,model=virtio,macaddr=$(utils/random-mac.py) \
  -chardev socket,id=chan0,path=$TMPDIR/rhev.sock,server,nowait \
  -chardev socket,id=chan1,path=$TMPDIR/qemu.sock,server,nowait \
  -device virtio-serial-pci \
  -device virtserialport,chardev=chan0,name=com.redhat.rhevm.vdsm \
  -device virtserialport,chardev=chan1,name=org.qemu.guest_agent.0 \
  -device vmware-svga \
  -vnc :0 \
  -usbdevice tablet \
  &>/dev/null &

echo QEMUPID=$!
utils/wait-ip.py $TMPDIR

rm -rf $TMPDIR
