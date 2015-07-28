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
rsync
qemu-guest-agent
-kexec-tools
%end

%post
eval $(tr ' ' '\n' < /proc/cmdline | grep =)

mkdir -m 0700 /root/.ssh
curl -so /root/.ssh/authorized_keys http://$APILISTENER/static/keys/demobuilder.pub
chcon system_u:object_r:ssh_home_t:s0 /root/.ssh /root/.ssh/authorized_keys

echo >/etc/udev/rules.d/75-persistent-net-generator.rules
sed -i -e '/^HWADDR=/ d' /etc/sysconfig/network-scripts/ifcfg-eth0
rm /etc/udev/rules.d/70-persistent-net.rules

sed -i -e 's/^timeout=.*/timeout=0/' /boot/grub/grub.conf

passwd -l root

cd /root
curl -so config http://$APILISTENER/static/config
curl -so vm-functions http://$APILISTENER/static/utils/vm-functions
. ./vm-functions

register_channels rhel-6-server-rpms
yum_update
cleanup

rm config vm-functions

%end
