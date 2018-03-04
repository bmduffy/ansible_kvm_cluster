# Create a virtual cluster with ansible

Create and manage a virtual clusters with `ansible`, `kvm` and `libvirt` on a
single machine.

This repository automates as much as possible the creation of a variety cluster
for testing and learning purposes.

## Minimum System Requirments

## Get Base Images

Use `osinfo-query os` to see a list of all supported OSs.

## Getting Started

The following will get you all the software you need to start creating
clusters. First install `ansible`;
```
>> yum install ansible
```
Then clone this git repo;
```
>> git clone https://github.com/bmduffy/ansible_kvm_cluster.git
```
The playbooks in this repo will need to interact with your `localhost` to
create virtual clusters. The following playbook will install `libvirt` on your
machine and restart it;
```
>> cd ansible_kvm_cluster/install
>> ansible-playbook site.yml
```

## Repository Strucutre

Common and reusable `ansible` is stored in `roles` and `plays`. The following
clusters are (will be) defined;

* `generic` - Basic `vm` cluster sans any cluster software
* `ocp` - Openshift Container Platfrom Enterprise edition
* `origin` - Openshift Origin free version
* `k8s` - Kubernetes cluster

## Create a Virtual cluster

Tasks carried out on clusters is managed by `ansible` tags;
```
>> ansible-playbook -i inventories/generic playbooks/provision.yml
```
