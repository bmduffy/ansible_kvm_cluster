#!/usr/bin/python

# https://libvirt.org/docs/libvirt-appdev-guide-python/en-US/html/

import libvirt

from ansible.module_utils.basic import AnsibleModule

def run_module():

    fields = dict(
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

    # return the result of the update
    module.exit_json(**result)


def main():
    run_module()

if __name__ == '__main__':
    main()
