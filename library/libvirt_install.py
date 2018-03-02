#!/usr/bin/python

import libvirt

from ansible.module_utils.basic import AnsibleModule

def run_module():

    fields = dict(
        domain = dict(type='str', required=True),
        name = dict(type='str', required=True),
        cpus = dict(type='int', required=True),
        memory = dict(type='int', required=True),
        nics = dict(type='list', required=True),
        boot_disk = dict(type='str', required=True),
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

    # check if the metadata is an update and generate any new data
    # update(module, result, data, meta_object.Node(**module.params))

    # return the result of the update
    module.exit_json(**result)


def main():
    run_module()

if __name__ == '__main__':
    main()
