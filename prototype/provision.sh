#!bin/bash

# check what sequence of commands is required to set up a libvirt VM

set -x

default_subdomain="ocp.cluster.ie"
root_password="passw0rd"
timezone="Europe/Dublin"
keyboard="ie"
sshd_config="sshd_config.j2"
img_path="/home/brian.duffy/libvirt/images"
ssh_key="/home/brian.duffy/.ssh/id_rsa.pub"
base_img="${img_path}/rhel-server-7.4-x86_64-kvm.qcow2"

host="test-vm1"
macaddr="52:54:00:00:00:01"
network="network0"

disk1="${img_path}/${host}-disk1.qcow2"
disk2="${img_path}/${host}-disk2.qcow2"

cp ${base_img} ${disk1}

virt-sysprep --connect qemu:///system \
  -a ${disk1} \
  --hostname ${host} \
  --root-password password:${root_password} \
  --ssh-inject root:file:${ssh_key} \
  --timezone ${timezone} \
  --upload ${sshd_config}:/etc/ssh/sshd_config \
  --uninstall cloud-init.x86_64 \
  --firstboot prep_host.sh

virt-install --connect qemu:///system \
  --import --name ${host} \
  --ram 1024 --vcpus 1 \
  --os-variant rhel7 \
  --disk path=${disk1},format=qcow2 \
  --disk path=${disk2},size=20,format=qcow2 \
  --network network=${network},model=virtio,mac=${macaddr} \
