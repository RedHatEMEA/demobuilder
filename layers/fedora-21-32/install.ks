authconfig --enableshadow --passalgo=sha512
bootloader --location=mbr
cdrom
clearpart --all
firewall --service=ssh
install
keyboard us
lang en_US
network --onboot yes --device eth0 --bootproto dhcp --noipv6
part / --fsoptions=discard --fstype=ext4 --grow --size=1
part swap --size=512
poweroff
rootpw redhat
text
timezone --utc UTC
zerombr

%packages --nobase
@core
iptables-services
rsync
qemu-guest-agent
%end

%post
exec &>/dev/console
set -x

eval $(tr ' ' '\n' < /proc/cmdline | grep =)

mkdir -m 0700 /root/.ssh
curl -so /root/.ssh/authorized_keys http://$APILISTENER/static/keys/demobuilder.pub
chcon system_u:object_r:ssh_home_t:s0 /root/.ssh /root/.ssh/authorized_keys

sed -i -e '/^HWADDR=/ d' /etc/sysconfig/network-scripts/ifcfg-eth0

sed -i -e 's/^  set timeout=.*/  set timeout=0/' /boot/grub2/grub.cfg

passwd -l root

cd /root
curl -so vm-functions http://$APILISTENER/static/utils/vm-functions
. ./vm-functions

systemctl enable iptables.service
systemctl enable network.service

register_channels
yum_remove 'NetworkManager*' firewalld
yum_update
cleanup

rm vm-functions

grubby --update-kernel=ALL --args=net.ifnames=0 --remove-args=console=ttyS0,115200n8

%end
