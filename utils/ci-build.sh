#!/bin/bash

exec ./build.py \
  rhel-server-7:gui:fuse-6.2:vagrant-libvirt \
  rhel-server-7:gui:fuse-6.2:vagrant-virtualbox \
  rhel-server-7:gui:ose-3.1:vagrant-libvirt \
  rhel-server-7:gui:ose-3.1:vagrant-virtualbox \
  rhel-server-7:gui:ose-3.1:offline:vagrant-libvirt \
  rhel-server-7:gui:ose-3.1:offline:vagrant-virtualbox \
  rhel-server-7:gui:ose-3.1:offline:demo:vagrant-libvirt \
  rhel-server-7:gui:ose-3.1:offline:demo:vagrant-virtualbox \
  rhel-server-7:gui:ose-3.1:offline:demo:aws \
  rhel-server-7:gui:rhelosp-7:vagrant-libvirt \
  fedora-21-32:gui:webex:vagrant-libvirt
