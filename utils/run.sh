#!/bin/bash

qemu-kvm -nodefaults \
  -m 1024 \
  -drive discard=unmap,file=$1,id=disk1,if=none \
  -device virtio-scsi-pci \
  -device scsi-disk,drive=disk1 \
  -net bridge,br=virbr0 \
  -net nic,model=virtio \
  -chardev socket,id=chan0,path=/tmp/$1-rhev.sock,server,nowait \
  -chardev socket,id=chan1,path=/tmp/$1-qemu.sock,server,nowait \
  -device virtio-serial-pci \
  -device virtserialport,chardev=chan0,name=com.redhat.rhevm.vdsm \
  -device virtserialport,chardev=chan1,name=org.qemu.guest_agent.0 \
  -cdrom ../../cache/download.eng.rdu2.redhat.com/released/RHEL-6/6.5/Server/x86_64/iso/RHEL6.5-20131111.0-Server-x86_64-DVD1.iso \
  -device vmware-svga \
  -display sdl &

../../utils/wait-ip.py $1

wait
