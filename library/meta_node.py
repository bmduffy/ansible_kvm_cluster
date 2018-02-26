#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: meta_cluster

short_description: This is module generates cluster variables based on host
file and group_vars configuration.

version_added: "2.4"

description:
    - "This is module generates cluster variables based on host
       file and group_vars configuration."
    - Only intended to run on `localhost`

options:
    path:
        description:
            - Where to store the metadata for this cluster
        required: true
    state:
        description:
            - Do you want the metadata to be `present` or `absent`
        required: false

author:
    - Brian Duffy (@bmduffy)
'''

EXAMPLES = '''
# Generate metadata from your `host_vars` and `group_vars`
- name: "Generate host variables for a given host"
  cluster_init:
    path: ~/.kvm/clusters/test.cluster
    state: present

# Remove metadata file for specified cluster
- name: "Ensure this cluster is present"
  cluster_init:
    path: "~/.kvm/clusters"
    domain: "test.cluster.local"
    state: present
'''

RETURN = '''
message:
    description: The output message that the sample module generates
'''

import os
import yaml
import copy
import random

from ansible.module_utils.basic import AnsibleModule

def update_networks(module, result, metadata, data):

    changed = False
    message = ""

    for name, subnet in networks.iteritems():
        network = "{}.{}".format(name, node.domain)
        if network not in networks:

    return changed, message

def update_node(module, result, metadata, data):

    changed = False
    message = ""


    if node.name not in nodes:
        changed = True
        message = "Adding '{}' to cluster '{}'".format(
                    node.name, node.domain)
        nics = []
        for n in node.nics:
            nics.append({
                "network":
                "model" : "virtio",
                "mac": get_a_mac_address(cluster),
                "ipv4": get_an_ipv4_address(),
            })

        disks = []
        for d in node.disks:
            disks.append({
                "format": d.get("format"),
                "size": d.get("size"),
            })

        nodes[node] = {
            "hostname": "{}.{}".format(node.name, node.domain),
            "cpus": node.cpus,
            "memory": node.memory,
            "disks":,
            "nics": nics,
        }
    else:
        print "check for updates to this node"

    return changed, message

def delete_node(module, result, metadata, data):

    item_type = metadata.get('type')
    cluster = data.get(metadata.get('domain'))
    node = data.get(metadata.get('node'))
    netowrk = data.get(metadata.get('network'))

    if item_type == "cluster":
        del data[cluster]
        result['changed'] = True
        result['message'] = "Removed '{}' cluster".format(cluster)
    elif item_type == "node":
        del data[cluster][node]
        result['changed'] = True
        result['message'] = "Removed '{}' node".format(node)
    elif item_type == "network":
        pass "how do you delete this??"

def update(module, result, data, node):

    result['changed'] = False
    result['message'] = "'{}' is up to date".format(metadata.name)

    data = read_data(path)

    if node.domain not in data:
        data[node.domain] = {"nodes":{}, "networks":{}}
    if metadata.state == 'present':
        update_node(module, result, metadata, data)
    elif metadata.state == 'absent':
        delete_node(module, result, metadata, data)

    meta_file.write_data(clusters)


def run_module():

    fields = dict(
        path = dict(type='str', required=True),
        domain = dict(type='str', required=True),
        name = dict(type='str', required=True),
        cpus = dict(type='int', required=True),
        memory = dict(type='int', required=True),
        nics = dict(type='list', required=True),
        root_disk = dict(type='str', required=False, default='20G'),
        extra_disks = dict(type='list', required=False, default=[]),
        state = dict(
            type = 'str',
            required = False,
            default='present',
            choices=['present', 'absent']
        )
    )

    result = dict(changed=False, message='')
    module = AnsibleModule(
        argument_spec=fields, supports_check_mode=True)

    if module.check_mode:
        return result

    # read any data that has already been generated
    data = meta_file.read_data(
        "{}/clusters.yml".format(
        os.path.expanduser(module.params['path'])))

    # check if the metadata is an update and generate any new data
    update(module, result, data, meta_object.Node(**module.params))

    # return the result of the update
    module.exit_json(**result)


def main():
    run_module()

if __name__ == '__main__':
    main()
