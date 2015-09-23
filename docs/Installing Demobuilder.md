# Installing Demobuilder

### Prerequisites

- Fedora 22 on a physical machine.

### Installation

```bash
# Install required packages
sudo dnf -y install git libcdio libguestfs libvirt pigz pyOpenSSL \
  python-bottle PyYAML qemu-kvm python-cherrypy python-apsw

# Ensure system is up to date
sudo dnf -y update

# Ensure required services are started
sudo systemctl enable libvirtd.service
sudo systemctl start libvirtd.service

# If using firewalld (on by default), allow VMs to communicate to the
# hypervisor
sudo firewall-cmd --permanent --zone=trusted --add-interface=virbr0
sudo firewall-cmd --reload

# Clone repository
cd $HOME
git clone --recursive https://github.com/RedHatEMEA/demobuilder.git

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
./build.sh rhel-server-7 rhel-server-7:gui rhel-server-7:gui:ose-3.0 \
  rhel-server-7:gui:ose-3.0:vagrant-libvirt
```
