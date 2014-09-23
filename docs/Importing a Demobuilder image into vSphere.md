# Importing a Demobuilder image into vSphere

### Prerequisites

You'll need to have the following:

- vCenter hostname (e.g. "vcenter.example.com")
- vCenter credentials (e.g. "myuser" and "mypassword")
- existing vCenter datacenter name (e.g. "mydatacenter")
- existing vCenter cluster name (e.g. "mycluster")
- existing vCenter datastore name (e.g. "mydatastore")
- existing vCenter network name (e.g. "My VM Network")

You'll need to make up the name of:

- a temporary imported VM image (e.g. "tempvm")

### Import process

1. Download and install [VMware Open Virtualization Format Tool](https://my.vmware.com/web/vmware/details?productId=352&downloadGroup=OVFTOOL350).

1. Substitute values and run ovftool as follows to import the Demobuilder image as a VMware VM image:

   ```bash
   $ ovftool --noSSLVerify --net:'VM Network=My VM Network' \
   --datastore=mydatastore --name=tempvm \
   build/rhel-server-6.5:gui:openshift:vsphere.ova \
   vi://myuser:mypassword@vcenter.example.com/mydatacenter/host/mycluster/
   ```

1. Convert the temporary VM image into a template:

   ```bash
   $ java -jar utils/vmwarecli.jar -h vcenter.example.com -u myuser \
   -p mypassword -k cloneVMtoTemplate mydatacenter/vm/tempvm \
   'OpenShift Template'
   ```

1. Remove the temporary VM image:

   ```bash
   $ java -jar utils/vmwarecli.jar -h vcenter.example.com -u myuser \
   -p mypassword -k deleteVM mydatacenter/vm/tempvm
   ```
