

class Cluster(object):
    def __init__(self, **kwargs):
        self.domain = kwargs.get('domain')
        self.state  = kwargs.get('state')


class Network(object):
    def __init__(self, **kwargs):
        self.name   = kwargs.get('name')
        self.subnet = kwargs.get('subnet')
        self.state  = kwargs.get('state')


class Node(object):
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.cpus = kwargs.get('cpus')
        self.memory = kwargs.get('memory')
        self.nics = kwargs.get('nics')
        self.root_disk = kwargs.get('root_disk')
        self.extra_disks = kwargs.get('extra_disks')
        self.state = kwargs.get('state')
