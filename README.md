# Create a virtual cluster with ansible

Create and manage a virtual cluster with `ansible`, `kvm` and `libvirt` on a
single machine.

This is useful for creating a virtual local cluster for testing, learning and
experimentation. This document will explain what is needed to achieve this and
by the time you are finished you should have a virtual cluster.

Why not use `vagrant`? Here are some reasons why I did it this way;

1. I want to learn virtualization technology, specifically `libvirt` and `qemu`.
2. `vagrant` creates two network interface cards (NICs) when only one is needed.
3. `vagrant` creates that default `vagrant` user that I don't want.
4. I want more control over my virtual machine images.
5. I want to define my cluster in `yaml` so that's why I use `ansible`.

## Create a base image to run on your cluster nodes

This section goes through how to create and

### Download a boot iso and create

* Create an image for whatever OS you want to use [here](
https://raymii.org/s/articles/virt-install_introduction_and_copy_paste_distro_install_commands.html).
* If you need a RHEL iso or guest image you will can get it [here](
https://access.redhat.com/downloads/content/69/ver=/rhel---7/7.4/x86_64/product-software).


You can use guestfish to edit a running system under `kvm` virtualization:
- You can use "guestfish" to edit the /etc/shadow file and change the root password.
- Guestfish is an interactive shell that you can use from the command line or from shell scripts to access guest virtual machine file systems. (See example below):

https://wiki.libvirt.org/page/VM_lifecycle
https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/7/html/Virtualization_Deployment_and_Administration_Guide/sect-Managing_guest_virtual_machines_with_virsh-Managing_virtual_networks.html#static-ip-address
https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/7/html/Virtualization_Deployment_and_Administration_Guide/sect-Guest_virtual_machine_installation_overview-Creating_guests_with_virt_install.html
https://fatmin.com/2016/12/20/how-to-resize-a-qcow2-image-and-filesystem-with-virt-resize/
