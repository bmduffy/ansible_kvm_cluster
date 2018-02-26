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

from ansible.module_utils.basic import AnsibleModule



def update(module, result, data, cluster):

    cluster_exists = "'{}' already exists"
    add_cluster    = "Added '{}' cluster domain"
    remove_cluster = "Removed '{}' cluster domain"

    if cluster.state == 'present':
        if data.get(cluster.domain) is None:
            result['changed'] = True
            result['message'] = add_cluster.format(cluster.domain)
            data[cluster.domain] = {
                "nodes":{},
                "networks":{},
            }
        else:
            result['changed'] = False
            result['message'] = cluster_exists.format(cluster.domain)

    elif metadata.state == 'absent':
        
    write_data(clusters)

def run_module():

    fields = dict(
        path     = dict(type='str',  required=True),
        domain   = dict(type='str',  required=True),
        name     = dict(type='str',  required=True),
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
    update(module, result, data, meta_object.Cluster(**module.params))

    # return the result of the update
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
