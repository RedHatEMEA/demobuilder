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
%end

%post
eval $(tr ' ' '\n' < /proc/cmdline | grep =)

mkdir -m 0700 /root/.ssh
curl -so /root/.ssh/authorized_keys http://$listener/keys/demobuilder.pub
chcon system_u:object_r:ssh_home_t:s0 /root/.ssh /root/.ssh/authorized_keys

sed -i -e '/^HWADDR=/ d' /etc/sysconfig/network-scripts/ifcfg-eth0

sed -i -e 's/^  set timeout=.*/  set timeout=0/' /boot/grub2/grub.cfg

for i in /etc/yum.repos.d/*.repo; do sed -i -e 's!^#baseurl=http://download.fedoraproject.org/!baseurl=http://www.mirrorservice.org/sites/dl.fedoraproject.org/!; s/^metalink=/#metalink=/' $i; done

passwd -l root

curl -so /root/vm-functions http://$listener/utils/vm-functions

. /root/vm-functions

http_proxy=$pxy yum_update
cleanup

rm /root/vm-functions

%end
