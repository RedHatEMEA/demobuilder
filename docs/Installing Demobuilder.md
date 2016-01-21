# Installing Demobuilder

### Prerequisites

- Fedora 22 or RHEL7, on a physical machine (at a pinch on a virtual machine
  with nested virtualisation enabled, but builds are not very reliable).

If using a virtual machine, suggested minimum specs are 8GB RAM and 50GB disk.

Note for OSX users: demobuilder is known to work with nested virtualisation in
VMware Fusion; VirtualBox and Parallels have been tried unsuccessfully (so far).
In VMware Fusion, select Settings / Processors & Memory / Advanced Options /
Enable hypervisor applications in this virtual machine.

### Installation

```bash
# Install required packages (Fedora)
sudo dnf -y install git libcdio libguestfs libvirt pigz pyOpenSSL \
  python-apsw python-pyasn1 python-bottle python-cherrypy PyYAML qemu-kvm

# Install required packages (RHEL)
sudo yum -y install git gcc libcdio libguestfs libvirt pigz pyOpenSSL \
  python-pyasn1 python-bottle python-cherrypy python-devel PyYAML.x86_64 \
  sqlite-devel qemu-kvm

# RHEL only: python-apsw is not yet available in RPM format although work is
# being done to add it to EPEL.
curl -sLO https://github.com/rogerbinns/apsw/archive/3.7.17-r1.zip
unzip -q 3.7.17-r1.zip
pushd apsw-3.7.17-r1
sudo python setup.py install
popd

# RHEL only: python-backports.ssl is not available in RPM format.
curl -sLO https://pypi.python.org/packages/source/b/backports.ssl/backports.ssl-0.0.9.tar.gz
tar -xzf backports.ssl-0.0.9.tar.gz
pushd backports.ssl-0.0.9
sudo python setup.py install
popd

# Ensure system is up to date
sudo dnf -y update

# Ensure required services are started
# If you get "Failed to execute operation: Access denied" you may have hit
# bz1224211.  Run sudo systemctl daemon-reexec and retry.
sudo systemctl enable libvirtd.service
sudo systemctl start libvirtd.service

# If using firewalld (on by default), allow VMs to communicate to the
# hypervisor
sudo firewall-cmd --permanent --zone=trusted --add-interface=virbr0
sudo firewall-cmd --reload

# Fork https://github.com/RedHatEMEA/demobuilder into your own GitHub account

# Clone your forked repository
cd $HOME
git clone --recursive https://github.com/<yourgithubid>/demobuilder.git

# Work through demobuilder's install-time checks
cd demobuilder
utils/init.sh

# Configure demobuilder
vi config.yml

# Add your RHN username and password to config.yml, and provide the UUID(s) of
# one or more pools to which VMs should be temporarily connected using
# subscription-manager at build time

# If building RHEL-based VMs, download appropriate ISOs to isos/.
mkdir isos
# download isos/rhel-server-6.7-x86_64-dvd, isos/rhel-server-7.2-x86_64-dvd.iso,
# etc.
```

### Building images

Note that **all** demobuilder scripts must be run from the root of the demobuilder directory tree.

```bash
cd demobuilder
./build.py
Usage: ./build.py layer[:target]...

Valid layers:
  centos-7
  centos-7:gui
  centos-7:gui:origin-1.1
  fedora-22
  fedora-22-32
  fedora-22-32:gui
  fedora-22-32:gui:webex
  fedora-22:demobuilder
  fedora-22:gui
  rhel-guest-image-6.6
  rhel-server-6
  rhel-server-6:gui
  rhel-server-7
  rhel-server-7:gui
  rhel-server-7:gui:aep-ea3
  rhel-server-7:gui:ose-3.1
  rhel-server-7:gui:ose-3.1:offline
  rhel-server-7:gui:ose-3.1:offline:demo

Valid targets:
  aws
  openstack
  rhev
  vagrant-libvirt
  vagrant-virtualbox
  vsphere

# Build an image
./build.py rhel-server-7:vagrant-libvirt
```
