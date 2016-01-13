# Installing Demobuilder

### Prerequisites

- Fedora 22 or RHEL7, on a physical or virtual machine (with nested
  virtualisation enabled).

If using a virtual machine, suggested minimum specs are 8GB RAM and 50GB disk.

Note for OSX users: demobuilder is known to work with nested virtualisation in
VMware Fusion; VirtualBox and Parallels have been tried unsuccessfully (so far).
In VMware Fusion, select Settings / Processors & Memory / Advanced Options /
Enable hypervisor applications in this virtual machine.

### Installation

```bash
# Install Red Hat CA certificates if required
# Download the certificates from https://mojo.redhat.com/docs/DOC-1049591
sudo mv redhat.com.crt redhat.com.engineering-services.crt /etc/pki/ca-trust/source/anchors
sudo update-ca-trust

# Install required packages
sudo dnf -y install git libcdio libguestfs libvirt pigz pyOpenSSL \
  python-bottle PyYAML qemu-kvm python-cherrypy python-apsw

# Install required packages using RHEL CSB:
$ sudo yum -y install git.x86_64 libcdio.x86_64 libguestfs.x86_64 libvirt.x86_64 pigz.x86_64 pyOpenSSL.x86_64 \
  python-bottle.noarch PyYAML.x86_64 qemu-kvm.x86_64 python-cherrypy.noarch python-apsw.x86_64

# [WARN] The 'python-apsw' RPM may not exist and need to be downloaded 
# and installed (http://bit.ly/1SOsJUB).
# $ cd $HOME/Downloads
# $ sudo yum -y install python-apsw-3.7.15.2.r1-1.el7.nux.x86_64.rpm

# [NOTE] If you encounter the error message "FATAL: please install python-backports.ssl", 
# you'll need to download and install 'backports.ssl' (http://bit.ly/1ZmoiFv).
# $ cd $HOME/Downloads
# $ gunzip -c backports.ssl-0.0.9.tar.gz | tar xf -
# $ cd backports.ssl-0.0.9
# $ sudo python setup.py install

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

# Configure demobuilder
cd demobuilder
cp config.yml.example config.yml

# Add your RHN username and password to config.yml, and provide the UUID(s) of
# one or more pools to which VMs should be temporarily connected using
# subscription-manager at build time

# If building RHEL-based VMs, download appropriate ISOs to isos/.
mkdir isos
# download isos/rhel-server-6.7-x86_64-dvd,
# isos/rhel-server-7.1-x86_64-dvd.iso, etc.
```

### Building images

Note that **all** demobuilder scripts must be run from the root of the demobuilder directory tree.

```bash
cd demobuilder
./build.sh
Usage: ./build.sh layer[:target]...

Valid layers:
  fedora-21
  fedora-21-32
  fedora-21-32:gui
  fedora-21-32:gui:webex
  fedora-21:gui
  rhel-guest-image-6.6
  rhel-server-6
  rhel-server-6:gui
  rhel-server-6:gui:ose-2.2
  rhel-server-7
  rhel-server-7:gui
  rhel-server-7:gui:ose-3.0
  rhel-server-7:gui:ose-3.0:demo-jminter

Valid targets:
  openstack
  rhev
  vagrant-libvirt
  vagrant-virtualbox
  vsphere

# Build an image
./build.sh rhel-server-7:gui:ose-3.0:vagrant-libvirt
```
