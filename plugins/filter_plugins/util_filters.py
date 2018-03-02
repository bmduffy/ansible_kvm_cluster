#!/usr/bin/python

import os

from ansible.errors import AnsibleError, AnsibleParserError


def expand(path):
    return os.path.expanduser(path)


def disk_size(string):
    return float(string.strip()[:-1])


class FilterModule(object):

    def filters(self):
        return {
            'expand'    : expand,
            'disk_size' : disk_size,
        }
