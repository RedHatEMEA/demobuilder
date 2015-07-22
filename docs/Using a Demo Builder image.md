### Fedora 22 instructions

As part of the 'vagrant up' when you start the OSE3.0 image, vagrant will try to export a local directoy to the virtual machine.
To make sure that the NFS export can work, and as NFS is a pain to configure for a firewall with sunrpc/mount/portmapper etc all needing ports to be opened; the suggestion is to add the virtual interfaces to the trusted network zone, this will allow all network traffic through to these internal networks.

NB we have assumed that the virtual interfaces are virbr0 and virbr1 that have been added by libvirt/vagrant.

~~~
firewall-cmd --permanent --add-interface="virbr0" --zone=trusted
firewall-cmd --permanent --add-interface="virbr1" --zone=trusted
firewall-cmd --complete-reload
~~~

That should open up the virbr-= ports.

