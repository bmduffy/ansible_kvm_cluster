# Write some extra filters for manipulating output
#
# Review:
# http://docs.ansible.com/ansible/latest/dev_guide/developing_plugins.html

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleError, AnsibleFilterError

def all_contain(data, string):
    """
        all_contain checks if all strings in a list
        contain a specified substring
    """
    return all([string in d for d in data])

def any_contain(data, string):
    """
        any_contain checks if any strings in a list
        contain a specified substring
    """
    return any([string in d for d in data])

class FilterModule(object):

    def filters(self):
        return {
            'all_contain': all_contain,
            'any_contain': any_contain,
        }
