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
    path: ~/.kvm/clusters/test.cluster
    state: present
'''

RETURN = '''
message:
    description: The output message that the sample module generates
'''

from ansible.module_utils.basic import AnsibleModule

def run_module():
    # define the available arguments/parameters that a user can pass to
    # the module
    module_args = dict(
        path=dict(type='str', required=True),
        state=dict(type='str', required=False, default='present')
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        message=''
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        return result

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    result['message'] = 'goodbye {} {}'.format(
        module.params['path'], module.params['state'])
   
    # use whatever logic you need to determine whether or not this module
    # made any modifications to your target
    # if module.params['new']:
    #     result['changed'] = True

    # during the execution of the module, if there is an exception or a
    # conditional state that effectively causes a failure, run
    # AnsibleModule.fail_json() to pass in the message and the result
    # if module.params['name'] == 'fail me':
    #     module.fail_json(msg='You requested this to fail', **result)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
