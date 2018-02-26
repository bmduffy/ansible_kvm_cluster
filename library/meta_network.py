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

import meta_file
import meta_objects
import ipv4
import macaddress

from ansible.module_utils.basic import AnsibleModule


def check_network_state(network, data):
    state = "unchanged"
    result = None
    if network.name not in data.get("networks"):
        state = "added"
        result = data["networks"][network.name] = generate_network_data(
                        "{}.{}".format(network.name, network.domain), network.subnet)
    else:
        current_state = data["networks"][network.name]


def update(module, result, data, network):

    result['changed'] = False
    result['message'] = "'{}' is up to date".format(network.name)

    if node.domain not in data:
        data[node.domain] = {"nodes":{}, "networks":{}}
    if metadata.state == 'present':
        if network.name not in data.get("networks"):
            result['changed'] = True
            result['message'] = "Adding network '{}'".format(network.name)
            data["networks"][network.name] = ipv4.calculate_subnet(
                network.subnet)
        else is_update(network, data):

    elif metadata.state == 'absent':
        delete_network(module, result, network, data)

    meta_file.write_data(clusters)


def run_module():

    fields = dict(
        path   = dict(type='str',  required=True),
        name   = dict(type='str',  required=True),
        domain = dict(type='str',  required=False),
        subnet = dict(type='str',  required=False),
        state  = dict(
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
    update(module, result, data, meta_object.Network(**module.params))

    # return the result of the update
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
