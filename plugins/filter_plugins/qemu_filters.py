#!/usr/bin/python

import os
import subprocess
from ansible.errors import AnsibleError, AnsibleParserError


def image_info(path):
    """
    Example Data:
    -------------
    image: node1.test.cluster.local.disk.1
    file format: qcow2
    virtual size: 8.0G (8589934592 bytes)
    disk size: 837M
    cluster_size: 65536
    Format specific information:
    compat: 0.10
    """
    if not os.path.isfile(path):
        raise AnsibleError("'{}' does not exist".format(path))
    qemu_img = "qemu-img info {}".format(path).split()
    process = subprocess.Popen(qemu_img, stdout=subprocess.PIPE)
    output = process.stdout.readlines()
    return {
        "image"  : output[0].split()[1],
        "format" : output[1].split()[2],
        "size"   : output[2].split()[2],
    }


class FilterModule(object):

    def filters(self):
        return {
            'image_info' : image_info,
        }
