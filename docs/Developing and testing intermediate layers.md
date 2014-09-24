# Developing and testing intermediate layers

### Intermediate layer build process

Building an intermediate layer is the most common build case in Demobuilder, and is the case which it is most likely that layer developers will want to duplicate, in order to add more layers.  The entire layer build process is implemented by Demobuilder in `utils/addlayer.sh`, and the layer developer is only responsible for providing the install executable to be run on the VM image, and any necessary supporting files.  The overall process works as follows:

1. Create a copy-on-write (COW) image of the base layer

1. Start a temporary virtual machine using the COW image and wait until its guest agent reports the VM's IP address to Demobuilder

1. Rsync the layer's `target/` directory to a temporary directory on the VM using the demobuilder SSH key

1. Run the `target/install` executable on the VM

1. Remove the target/ directory from the VM

1. Remove references to the VM MAC address from the VM

1. Power off the VM

### Intermediate layer definition

Each layer definition occupies a separate subdirectory under `layers/`.  This subdirectory contains a standard set of files which are used to define and build the layer.  A template intermediate layer which can be copied and reused can be found at `layers/template`.

As a minimum, an intermediate layer includes the following files:

- **`README`**: required, information about the layer including its name and contact details for the maintainer
- **`install`**: required, an executable file which creates the new layer as defined above.  For intermediate layers this should be a symlink to `../../utils/addlayer.sh`
- **`target/`**: required, a directory which is copied in its entirety to the the temporary VM during the layer build process
- **`target/install`**: required, an executable file which runs in the context of the VM to install the layer
- **`target/vm-functions`**: optional, should be a symlink to `../../../utils/vm-functions`.  If `target/install` is a shell script, it can source `vm-functions` to use a standard library of install routines provided by Demobuilder

### Creating a new intermediate layer

The following steps should be taken to create a new intermediate layer:

1. Determine a parent stack upon which you intend your new intermediate child layer to be added.  This will be a base layer, e.g. *rhel-server-6.5*, with zero or more layers already added, e.g. *rhel-server-6.5:gui*

1. Copy the template intermediate layer `layers/template` to a new subdirectory of your choice under `layers/`

1. Start a temporary COW VM of your parent stack (see below for how to do this) and work out the commands that will be necessary to install the additional components that will be provided by your new intermediate layer

1. Iterate the following process until you are happy with your new intermediate layer:

   1. Update `target/install` in your new intermediate layer to run the necessary commands to install the layer.  If you need to copy configuration files from your layer definition into the VM, place these files in the `target/` directory as well; they will be accessible in $PWD when `target/install` is run for you at build time.

   1. Test the build of a stack including your new intermediate layer, for example:

      ```bash
      $ rm -f build/rhel-server-6.5:gui:mynewlayer.qcow2
      $ ./build.sh rhel-server-6.5:gui:mynewlayer
      ```

   1. If the build succeeds, start a temporary COW VM of your new stack (see below for how to do this) to verify its functionality

1. Update the README file in the new layer to indicate the new layer's functionality and maintainers

1. Optionally, add one or more files to `targets/` defining the finalized stacks including your new layer that should be built by `./build.sh`.  These are files whose name represents the entire stack, e.g. `rhel-server-6.5:gui:mynewlayer:rhev`, and which contain environment variables which are read by the finalizing layer, for example to set the amount of memory required by the finalized VM image

1. Send a pull request to have the new layer included in the upstream demobuilder distribution :-)

### Running a temporary COW VM of a stack for test purposes

During the process of developing a new intermediate layer, it is likely that you will want to run a temporary VM of a parent stack, or of a stack which includes the layer that you're working on.  This section explains how to do this using the utilities provided by Demobuilder.

**IMPORTANT NOTE**: **never** start a temporary VM backed directly by a disk image from the `build/` directory.  This is important for two reasons:

1. Disk images in `build/` may have child COW images chained from them.  If this is the case, modifying the parent image is highly likely to corrupt all the chained child images.

1. Even if you know that the disk image you are working with does not have any child COW images, it is much more convenient to start a temporary VM backed by a temporary COW image of your disk image.  This makes it trivial to revert changes made during testing.

The following process can be used to create a temporary COW VM of a stack for test purposes:

1. Build the appropriate stack:

   ```bash
   $ ./build.sh rhel-server-6.5:gui:mynewlayer
   ```

1. Create a temporary COW snapshot file backed by the stack disk image:

   ```bash
   $ utils/createsnap.sh build/rhel-server-6.5:gui:mynewlayer mysnap
   ```

1. Run a temporary VM based on the temporary COW snapshot:

   ```bash
   $ utils/run.sh mysnap
   QEMUPID=xxxxx
   IP=192.168.122.xxx
   ```

1. Connect to your VM:

   - Using VNC to connect to your VM console:

      ```bash
      $ vncviewer localhost:0
      ```

   - Using SSH to connect to the VM:

      ```bash
      $ utils/ssh.sh root@$IP
      ```

1. When finished, kill the temporary VM and remove the temporary COW snapshot:

   ```bash
   $ kill $QEMUPID
   $ rm mysnap
   ```
