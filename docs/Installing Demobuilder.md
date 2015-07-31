# Installing Demobuilder

### Prerequisites

- Fedora 21 on a physical machine.

### Installation

```bash
# Run the following commands as root...

# Install required packages
$ yum -y install git libcdio libguestfs-tools-c libvirt python-markdown2 qemu

# Ensure all necessary CA certificates are correctly installed
$ pushd /etc/pki/ca-trust/source/anchors
$ wget http://path/to/ca.crt
$ popd
$ update-ca-trust

# Ensure system is up to date
$ yum -y update

# Ensure required services are started
$ systemctl enable libvirtd.service
$ systemctl start libvirtd.service

# If using firewalld (on by default), allow VMs to communicate to the
# hypervisor
$ firewall-cmd --permanent --zone=trusted --add-interface=virbr0
$ firewall-cmd --reload

# Clone repository
$ git clone https://github.com/RedHatEMEA/demobuilder.git
```

### Building images

Note that **all** demobuilder scripts must be run from the root of the demobuilder directory tree.

```bash
$ cd demobuilder
$ ./build.sh
Usage: ./build.sh layer|-a [target|-a]

Valid layers:
  foo
  foo:bar
  baz

Valid targets:
  openstack
  rhev
  vagrant
  vsphere

# Build a single image
$ ./build.sh foo openstack

# Build all images
$ ./build.sh -a
```

### Notes

1. If you get the following libguestfs errors, running `yum -y update` appears to resolve the problem.

   ```bash
   libguestfs: warning: supermin-helper -f checksum returned a short string
   libguestfs: error: cannot find any suitable libguestfs supermin, fixed or old-style appliance on LIBGUESTFS_PATH (search path: /usr/lib64/guestfs)
   ```
