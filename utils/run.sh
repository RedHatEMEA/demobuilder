#!/bin/bash -x

TMPDIR=$(mktemp -d)

qemu-kvm -nodefaults \
  -smp 4 \
  -m 4096 \
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
  -display sdl \
  &>/dev/null &

echo QEMUPID=$!
utils/wait-ip.py $TMPDIR

rm -rf $TMPDIR
