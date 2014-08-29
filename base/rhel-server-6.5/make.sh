#!/bin/bash

ROOT=$(realpath ../..)
. $ROOT/config
. $ROOT/utils/functions

mkbuild

ISO=$(cache https://download.eng.rdu2.redhat.com/released/RHEL-6/6.5/Server/x86_64/iso/RHEL6.5-20131111.0-Server-x86_64-DVD1.iso)

for FILE in initrd.img vmlinuz; do
  iso-read -i $ISO -e isolinux/$FILE -o build/$FILE
done

eval $($ROOT/utils/httpserver.py -r $ROOT -i $BRIDGE)
RELPATH=$(realpath . --relative-base=$ROOT)

qemu-img create -f qcow2 build/rhel-server-6.5-uncompressed.qcow2 10G
qemu-kvm -nodefaults \
  -display none \
  -m 512 \
  -kernel build/vmlinuz \
  -initrd build/initrd.img \
  -append "ks=http://$LISTENER/$RELPATH/rhel-server-6.5.ks listener=$LISTENER" \
  -device virtio-scsi-pci \
  -drive discard=unmap,file=build/rhel-server-6.5-uncompressed.qcow2,id=disk1,if=none \
  -device scsi-disk,drive=disk1 \
  -net bridge,br=$BRIDGE \
  -net nic,model=virtio,macaddr=$($ROOT/utils/random-mac.py) \
  -cdrom $ISO

rm build/vmlinuz build/initrd.img

kill $HTTPSERVERPID

qemu-img convert -cp -O qcow2 build/rhel-server-6.5-uncompressed.qcow2 build/rhel-server-6.5.qcow2

rm build/rhel-server-6.5-uncompressed.qcow2
