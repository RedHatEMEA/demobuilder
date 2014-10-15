authconfig --enableshadow --passalgo=sha512
bootloader --location=mbr
cdrom
firewall --service=ssh
install
keyboard uk
lang en_GB.UTF-8
network --onboot yes --device eth0 --bootproto dhcp --noipv6
clearpart --all
part / --fsoptions=discard --fstype=ext4 --grow --size=1
part swap --size=512
poweroff
rootpw redhat
text
timezone --utc Europe/London
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
%end
